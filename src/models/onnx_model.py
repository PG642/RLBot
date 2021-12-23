import onnx
import onnxruntime
import numpy as np

class ONNXModel():
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = onnx.load(model_path)
        self.session = onnxruntime.InferenceSession(model_path, None)

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[2].name

        self.is_continuous = self.output_name == 'continuous_actions'
        self.is_multi_discrete = self.output_name == 'discrete_actions'

    def run(self, data):
        if self.is_continuous:
            return self.session.run([self.output_name], {self.input_name: data})
        elif self.is_multi_discrete:
            return self.session.run([self.output_name], {self.input_name: data, 'action_masks': np.array([[1] * 26], dtype=np.float32)})
        else:
            raise NotImplementedError

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
        return self.session.get_outputs()[2].shape
