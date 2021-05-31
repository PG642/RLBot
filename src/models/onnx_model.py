import onnx
import onnxruntime


class ONNXModel():
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = onnx.load(model_path)
        self.session = onnxruntime.InferenceSession(model_path, None)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def run(self, data):
        return self.session.run([self.output_name], {self.input_name: data})

    def check(self):
        try:
            onnx.checker.check_model(self.model)
        except onnx.checker.ValidationError as e:
            print('The model is invalid: %s' % e)
        else:
            print('The model is valid!')

    def get_input_shape(self):
        return self.session.get_inputs()[0].shape

    def get_output_shape(self):
        return self.session.get_outputs()[0].shape
