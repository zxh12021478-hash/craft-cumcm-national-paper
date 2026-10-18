# Task B — 可替换英文 Summary（替换 paper.md 中现有 "## Summary" 全段）

## Summary

This synthetic micro-case compares two temperature fields on a 2×2 grid, selects a heater policy under a simulated thermal-discomfort proxy, and tests that choice under a deterministic parameter perturbation. No experiment, electrical meter, executable code, or measured reference is involved.

For Q1, the model field [[10,20],[10,20]] and the commercial-CFD field [[20,10],[20,10]] share the same range [10, 20] °C and the same mean (15 °C), but they disagree at every matched grid cell: the exact cell-wise agreement rate is 0/4, with MAE and RMSE both 10 °C and a cell-wise correlation of −1. The range-overlap indicator is 1, but it measures only global range overlap rather than spatial agreement. Because the CFD result is itself a simulation sharing the assumed boundary conditions, it supports a code-to-code comparison only and cannot experimentally validate the model.

For Q2, at the base parameter p, policy H attains the lower simulated discomfort score among the two tested policies (H = 80, J = 90, baseline = 100), a 20% reduction in the proxy score relative to baseline. The proxy is neither electrical energy nor cost; therefore no measured electricity saving is claimed.

For Q3, [0.95p0, 1.05p0] is a deterministic parameter range, not a statistical confidence interval. At the tested upper endpoint, the ranking reverses (J = 92 < H = 105), so H is recommended only for the base setting and J at that endpoint. The lower endpoint, intermediate parameter values, and external operating conditions remain untested; physical validation is required before any real-world or energy-saving claim.

---

## 实际核查范围（本摘要据何写成）

- **仅阅读** forward-input/ 的 paper.md 与 results.json；二者数值交叉核对一致：Q1 两个场数组与 range_overlap=1；Q2 baseline=100、H=80、J=90，20% 经复算 (100−80)/100=0.2 与 JSON 一致；Q3 乘数 [0.95,1.05]、上端点 H=105/J=92、probability_model=null。
- **执行了一个标准库短检查** probe_B.py → probe_B_result.json：按匹配网格单元计算一致率、MAE、RMSE、均值、范围、逐元相关，并核对 Q2/Q3 排序。
- **未做**：联网、安装、模拟运行；未读代码/PDF/实验数据（材料声明均不存在）；未检查 0.95p0 下端点、中间参数、外部工况（未提供）；未做代理分到电量的换算（无模型）。
- 与 Task A 的材料互不相关，证据未混用。
- 详细问题清单与未核查项见 audit-B.md。
