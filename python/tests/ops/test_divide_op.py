#!/usr/bin/env python3

# Copyright (c) 2021 CINN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import numpy as np
from op_test import OpTest, OpTestTool
from op_test_helper import TestCaseHelper
import paddle
import paddle.nn.functional as F
import cinn
from cinn.frontend import *
from cinn.common import *


@OpTestTool.skip_if(not is_compiled_with_cuda(),
                    "x86 test will be skipped due to timeout.")
class TestDivOp(OpTest):
    def setUp(self):
        print(f"\nRunning {self.__class__.__name__}: {self.case}")
        self.init_case()

    def init_case(self):
        self.x_np = self.random(
            shape=self.case["x_shape"],
            dtype=self.case["x_dtype"],
            low=-10,
            high=10)
        self.y_np = self.random(
            shape=self.case["y_shape"],
            dtype=self.case["y_dtype"],
            low=1,
            high=10)

    def build_paddle_program(self, target):
        x = paddle.to_tensor(self.x_np, stop_gradient=True)
        y = paddle.to_tensor(self.y_np, stop_gradient=True)

        out = paddle.divide(x, y)

        self.paddle_outputs = [out]

    def build_cinn_program(self, target):
        builder = NetBuilder("div")
        x = builder.create_input(
            self.nptype2cinntype(self.case["x_dtype"]), self.case["x_shape"],
            "x")
        y = builder.create_input(
            self.nptype2cinntype(self.case["y_dtype"]), self.case["y_shape"],
            "y")
        out = builder.divide(x, y)

        prog = builder.build()
        res = self.get_cinn_output(prog, target, [x, y],
                                   [self.x_np, self.y_np], [out])

        self.cinn_outputs = [res[0]]

    def test_check_results(self):
        max_relative_error = self.case[
            "max_relative_error"] if "max_relative_error" in self.case else 1e-5
        self.check_outputs_and_grads(max_relative_error=max_relative_error)


class TestDivAll(TestCaseHelper):
    def init_attrs(self):
        self.class_name = "TestDivOpCase"
        self.cls = TestDivOp
        self.inputs = [
            {
                "x_shape": [32],
                "y_shape": [32],
            },
            {
                "x_shape": [32, 64],
                "y_shape": [32, 64],
            },
            {
                "x_shape": [2, 3, 4],
                "y_shape": [1, 5, 2],
            },
            {
                "x_shape": [2, 2, 32],
                "y_shape": [32],
            },
            {
                "x_shape": [16, 8, 4, 2],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [16, 8, 4, 2, 1],
                "y_shape": [16, 8, 4, 2, 1],
            },
        ]
        self.dtypes = [
            {
                "x_dtype": "int32",
                "y_dtype": "int32",
            },
            {
                "x_dtype": "int64",
                "y_dtype": "int64",
            },
            {
                "x_dtype": "float32",
                "y_dtype": "float32",
            },
            {
                "x_dtype": "float64",
                "y_dtype": "float64",
            },
        ]
        self.attrs = []


if __name__ == "__main__":
    TestDivAll().run()
