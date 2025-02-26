'''Copyright The Microsoft DeepSpeed Team'''

import pytest
import torch
from deepspeed.runtime.zero.linear import LinearModuleForZeroStage3
from unit.common import DistributedTest


@pytest.mark.parametrize('half_op', [False, True])
class TestAutoCastDisable(DistributedTest):
    def test_missing_amp_autocast(self, half_op):
        hidden_dim = 4
        if half_op:
            input = torch.randn(hidden_dim).cuda().half()
            ds_linear = LinearModuleForZeroStage3(hidden_dim, hidden_dim).cuda().half()
        else:
            input = torch.randn(hidden_dim).cuda()
            ds_linear = LinearModuleForZeroStage3(hidden_dim, hidden_dim).cuda()

        output = ds_linear(input)
        assert output.dtype == ds_linear.weight.dtype

    def test_disable_autocast_linear(self, half_op):
        amp = pytest.importorskip("torch.cuda.amp")

        hidden_dim = 4
        if half_op:
            input = torch.randn(hidden_dim).cuda().half()
            ds_linear = LinearModuleForZeroStage3(hidden_dim, hidden_dim).cuda().half()
        else:
            input = torch.randn(hidden_dim).cuda()
            ds_linear = LinearModuleForZeroStage3(hidden_dim, hidden_dim).cuda()

        with amp.autocast(False):
            output = ds_linear(input)
            assert output.dtype == ds_linear.weight.dtype


@pytest.mark.parametrize('half_input, half_weight',
                         [(False,
                           False),
                          (False,
                           True),
                          (True,
                           False),
                          (True,
                           True)])
class TestAutoCastEnable(DistributedTest):
    def test_autocast_linear(self, tmpdir, half_input, half_weight):
        amp = pytest.importorskip("torch.cuda.amp")

        hidden_dim = 4
        input = torch.randn(hidden_dim).cuda()
        ds_linear = LinearModuleForZeroStage3(hidden_dim, hidden_dim).cuda()

        if half_input:
            input = input.half()

        if half_weight:
            ds_linear = ds_linear.half()

        with amp.autocast():
            output = ds_linear(input)
            assert output.dtype == torch.half
