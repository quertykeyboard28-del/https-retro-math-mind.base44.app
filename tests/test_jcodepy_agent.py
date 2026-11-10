from jcodepy_agent import JCodePyAgentCore


def test_memory_lookup_and_no_false_generation(tmp_path):
    agent = JCodePyAgentCore(kb_path=tmp_path / "kb.json")
    assert "WiCi One" in agent.respond_to("What is WiCi One?")
    assert "No sufficiently similar" in agent.respond_to("unrelated topic zebra")


def test_volume_calculation():
    result = JCodePyAgentCore.kalkul8_dual_volume_analysis(2, 3, 4, 1, 1, 2)
    assert result["volume_box_a"] == 24
    assert result["surface_box_a"] == 52
    assert result["ratio_a_to_b"] == 12
    assert result["volumetric_variance"] == 22


def test_invalid_dimensions_rejected():
    try:
        JCodePyAgentCore.kalkul8_dual_volume_analysis(-1, 2, 3, 1, 1, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative dimension should fail")
