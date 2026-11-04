"""Sharper pictures: Real-ESRGAN x4plus (4x AI upscaling) without PyTorch, for the client's ChatGPT
images, which come at about 1.7k px while the page heads need 2.4-3.2k on sharp screens. The official
weights (.pth, a zip of pickled tensors) are read with a restricted unpickler (only tensor rebuilding is
allowed), the RRDBNet is built as an ONNX graph and run tile by tile with onnxruntime on the CPU
(about 5 minutes for 1672 x 941 on 4 cores). Not part of the site.

Setup (once per container, outside the repo):
  python3 -m venv venv && venv/bin/pip install --only-binary=:all: "onnx>=1.18,<1.21" "onnxruntime>=1.20,<1.24" "numpy<2.4" pillow
  curl -L -o RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
  sha256: 4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1
Run:
  venv/bin/python -I tools/upscale.py RealESRGAN_x4plus.pth <input.png> <output-x4.png> [tile=256] [pad=16]
Then check the product (lettering, chargers, hatches, frame, wheels) and resize the x4 result down to
the published widths (Lanczos), WebP + JPEG.
"""
import io, pickle, sys, time, zipfile
from collections import OrderedDict

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort
from PIL import Image


# ------------------------------------------------------------------ the weights, without torch
class _Storage:
    def __init__(self, dtype, key):
        self.dtype, self.key = dtype, key


DTYPES = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'DoubleStorage': np.float64}


def load_pth(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    pkl = next(n for n in names if n.endswith('data.pkl'))
    base = pkl[: -len('data.pkl')]
    cache = {}

    def rebuild(storage, offset, size, stride, *rest):
        if storage.key not in cache:
            cache[storage.key] = np.frombuffer(z.read(f'{base}data/{storage.key}'), dtype=storage.dtype)
        flat = cache[storage.key]
        n = int(np.prod(size)) if size else 1
        arr = flat[offset: offset + n] if tuple(stride) == tuple(contiguous_strides(size)) else None
        if arr is None:
            arr = np.lib.stride_tricks.as_strided(flat[offset:], shape=size,
                                                  strides=[s * flat.itemsize for s in stride]).copy()
        return np.array(arr, dtype=np.float32).reshape(size)

    class Restricted(pickle.Unpickler):
        def find_class(self, module, name):
            if module == 'torch._utils' and name == '_rebuild_tensor_v2':
                return rebuild
            if module == 'collections' and name == 'OrderedDict':
                return OrderedDict
            if module == 'torch' and name in DTYPES:
                return name
            raise pickle.UnpicklingError(f'refused: {module}.{name}')

        def persistent_load(self, pid):
            kind, storage_type, key, location, numel = pid
            assert kind == 'storage'
            return _Storage(DTYPES[storage_type], key)

    data = Restricted(io.BytesIO(z.read(pkl))).load()
    return data


def contiguous_strides(size):
    st, acc = [], 1
    for d in reversed(size):
        st.append(acc); acc *= d
    return list(reversed(st))


# ------------------------------------------------------------------ RRDBNet (scale 4) as ONNX
def build_onnx(sd, num_block=23):
    nodes, inits = [], []
    counter = [0]

    def name(p):
        counter[0] += 1
        return f'{p}_{counter[0]}'

    def const(v):
        n = name('c'); inits.append(numpy_helper.from_array(np.array(v, dtype=np.float32), n)); return n

    def conv(x, key):
        w, b = sd[key + '.weight'], sd[key + '.bias']
        wn, bn = key + '.w', key + '.b'
        inits.append(numpy_helper.from_array(w.astype(np.float32), wn))
        inits.append(numpy_helper.from_array(b.astype(np.float32), bn))
        out = name('conv')
        nodes.append(helper.make_node('Conv', [x, wn, bn], [out], kernel_shape=[3, 3], pads=[1, 1, 1, 1]))
        return out

    def lrelu(x):
        out = name('lr'); nodes.append(helper.make_node('LeakyRelu', [x], [out], alpha=0.2)); return out

    def cat(xs):
        out = name('cat'); nodes.append(helper.make_node('Concat', xs, [out], axis=1)); return out

    def scaled_add(a, b, s=0.2):   # a * s + b
        m = name('mul'); nodes.append(helper.make_node('Mul', [a, const(s)], [m]))
        out = name('add'); nodes.append(helper.make_node('Add', [m, b], [out])); return out

    def add(a, b):
        out = name('add'); nodes.append(helper.make_node('Add', [a, b], [out])); return out

    def up2(x):
        out = name('up')
        nodes.append(helper.make_node('Resize', [x, '', const([1, 1, 2, 2])], [out], mode='nearest',
                                      coordinate_transformation_mode='asymmetric', nearest_mode='floor'))
        return out

    def rdb(x, p):
        x1 = lrelu(conv(x, p + '.conv1'))
        x2 = lrelu(conv(cat([x, x1]), p + '.conv2'))
        x3 = lrelu(conv(cat([x, x1, x2]), p + '.conv3'))
        x4 = lrelu(conv(cat([x, x1, x2, x3]), p + '.conv4'))
        x5 = conv(cat([x, x1, x2, x3, x4]), p + '.conv5')
        return scaled_add(x5, x)

    feat = conv('x', 'conv_first')
    h = feat
    for i in range(num_block):
        p = f'body.{i}'
        o = rdb(h, p + '.rdb1'); o = rdb(o, p + '.rdb2'); o = rdb(o, p + '.rdb3')
        h = scaled_add(o, h)
    feat = add(feat, conv(h, 'conv_body'))
    feat = lrelu(conv(up2(feat), 'conv_up1'))
    feat = lrelu(conv(up2(feat), 'conv_up2'))
    out = conv(lrelu(conv(feat, 'conv_hr')), 'conv_last')
    nodes.append(helper.make_node('Identity', [out], ['y']))
    g = helper.make_graph(nodes, 'rrdbnet_x4',
                          [helper.make_tensor_value_info('x', TensorProto.FLOAT, [1, 3, 'h', 'w'])],
                          [helper.make_tensor_value_info('y', TensorProto.FLOAT, [1, 3, 'H', 'W'])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid('', 17)])
    m.ir_version = 8
    return m


# ------------------------------------------------------------------ run, tile by tile
def main():
    wpath, src, dst = sys.argv[1:4]
    tile = int(sys.argv[4]) if len(sys.argv) > 4 else 256
    pad = int(sys.argv[5]) if len(sys.argv) > 5 else 16
    data = load_pth(wpath)
    sd = data.get('params_ema') or data.get('params') or data
    print('weights:', len(sd), 'tensors')
    model = build_onnx(sd)
    onnx.checker.check_model(model)
    so = ort.SessionOptions(); so.intra_op_num_threads = 4
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess = ort.InferenceSession(model.SerializeToString(), so, providers=['CPUExecutionProvider'])
    img = np.asarray(Image.open(src).convert('RGB'), dtype=np.float32) / 255.0
    H, W, _ = img.shape
    out = np.zeros((H * 4, W * 4, 3), dtype=np.float32)
    t0 = time.time(); n = 0
    ys, xs = list(range(0, H, tile)), list(range(0, W, tile))
    total = len(ys) * len(xs)
    for y in ys:
        for x in xs:
            y0, x0 = max(0, y - pad), max(0, x - pad)
            y1, x1 = min(H, y + tile + pad), min(W, x + tile + pad)
            inp = img[y0:y1, x0:x1].transpose(2, 0, 1)[None]
            res = sess.run(['y'], {'x': inp})[0][0].transpose(1, 2, 0)
            ty, tx = (y - y0) * 4, (x - x0) * 4
            th, tw = min(tile, H - y) * 4, min(tile, W - x) * 4
            out[y * 4: y * 4 + th, x * 4: x * 4 + tw] = res[ty: ty + th, tx: tx + tw]
            n += 1
            if n == 1 or n % 6 == 0:
                print(f'tile {n}/{total}  {time.time() - t0:.0f}s', flush=True)
    Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)).save(dst)
    print('done', dst, out.shape, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
