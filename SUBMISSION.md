# Báo Cáo Nộp Bài Day 9 - Multi-Agent, A2A, LangGraph

## 1. Tổng quan bài làm

Bài nộp này hoàn thành Day 9 Lab về **Multi-Agent System**, sử dụng codebase A2A/LangGraph có sẵn trong repo.

Hệ thống được xây dựng theo kiến trúc **distributed multi-agent system**, gồm các thành phần chính:

- **Customer Agent**: nhận câu hỏi từ người dùng.
- **Law Agent**: phân tích pháp lý tổng quát và điều phối specialist agents.
- **Tax Agent**: xử lý các vấn đề liên quan đến thuế.
- **Compliance Agent**: xử lý các vấn đề compliance/regulatory.
- **Registry Service**: dùng để đăng ký và khám phá agents thông qua dynamic discovery.
- **A2A Protocol**: dùng để giao tiếp giữa các agents qua HTTP.
- **LangGraph**: dùng để xây dựng workflow, routing, parallel execution và aggregation.
- **Trace propagation**: truyền `trace_id`, `context_id`, và `delegation_depth` qua toàn bộ agent chain.
- **Failure handling**: kiểm thử khi Tax Agent bị tắt nhưng hệ thống vẫn tiếp tục xử lý.
- **Latency optimization**: đo và tối ưu thời gian phản hồi end-to-end.

---

## 2. Các yêu cầu đã hoàn thành

## Stage 1 - Direct LLM

Đã kiểm tra stage baseline với một LLM call trực tiếp.

Command:

```bash
uv run python stages/stage_1_direct_llm/main.py
```

Mục tiêu của stage này là so sánh với các stage sau, khi hệ thống được nâng cấp từ direct LLM thành tool-using agent và multi-agent system.

---

## Exercise 2 - Tools và Knowledge Base

Đã hoàn thành Exercise 2 bằng cách bổ sung knowledge base và tool mới.

Các thay đổi chính:

- Thêm legal knowledge entry cho thời hiệu khởi kiện vi phạm hợp đồng.
- Thêm tool `check_statute_of_limitations`.
- Thêm tool mới vào danh sách tools.
- Thêm logic xử lý tool call.
- Đảm bảo kết quả trả về có thông tin đúng về thời hiệu 3 năm.

Command kiểm thử:

```bash
uv run python exercises/exercise_2_tools.py
```

Kết quả kiểm thử:

```text
Câu hỏi: Thời hiệu khởi kiện vụ vi phạm hợp đồng là bao lâu?

🔧 Gọi tool: check_statute_of_limitations

✅ Kết quả:
Thời hiệu khởi kiện vụ vi phạm hợp đồng là 3 năm, tính từ ngày người có quyền yêu cầu biết hoặc phải biết quyền và lợi ích hợp pháp của mình bị xâm phạm.
```

Kết luận:

Exercise 2 pass vì agent đã gọi đúng tool và trả về kết quả có nội dung “3 năm”.

---

## Stage 3 - Single Agent ReAct

Đã hoàn thành Stage 3 với mô hình **Single Agent ReAct Loop**.

Đã bổ sung tool mới:

- `search_case_law`

Tool này dùng để tra cứu case law liên quan đến câu hỏi pháp lý.

Command kiểm thử:

```bash
uv run python stages/stage_3_single_agent/main.py
```

Câu hỏi kiểm thử:

```text
A company breached a contract and caused foreseeable lost profits. What are the legal consequences? Include relevant case law.
```

Agent đã gọi các tools:

```text
Tool: search_legal_database
Tool: search_case_law
```

Kết quả từ `search_case_law`:

```text
Hadley v. Baxendale (1854) - Consequential damages for breach of contract.
Carlill v. Carbolic Smoke Ball Co (1893) - Unilateral contract.
```

Kết luận:

Stage 3 pass vì agent đã tự quyết định gọi tool `search_case_law` trong ReAct loop và đưa case law vào final answer.

---

## Exercise 4 - Multi-Agent với Privacy Agent

Đã hoàn thành Exercise 4 bằng cách mở rộng in-process multi-agent system.

Các thay đổi chính:

- Thêm `privacy_agent`.
- Thêm routing logic cho các câu hỏi liên quan đến:
  - data
  - privacy
  - GDPR
  - dữ liệu
  - rò rỉ dữ liệu
- Sửa conditional routing để route đến Privacy Agent khi cần.
- Sửa aggregation để tổng hợp thêm privacy analysis.

Command kiểm thử:

```bash
uv run python exercises/exercise_4_multiagent.py
```

Câu hỏi kiểm thử:

```text
Nếu công ty bị rò rỉ dữ liệu khách hàng, hậu quả pháp lý và thuế là gì?
```

Kết quả kiểm thử cho thấy final answer có đủ các phần:

- Phân tích pháp lý.
- Phân tích thuế.
- Nghĩa vụ bảo vệ dữ liệu.
- Rủi ro privacy/data protection.

Kết luận:

Exercise 4 pass vì hệ thống đã route đúng đến Privacy Agent và tổng hợp kết quả vào final answer.

---

## Stage 4 - In-Process Multi-Agent System

Đã kiểm thử Stage 4 với kiến trúc multi-agent chạy trong cùng một process.

Command kiểm thử:

```bash
uv run python stages/stage_4_milti_agent/main.py
```

Lưu ý: folder trong repo gốc có tên `stage_4_milti_agent`, nên giữ nguyên tên này.

Workflow của Stage 4:

```text
analyze_law
→ check_routing
→ call_tax_specialist + call_compliance_specialist
→ aggregate
→ END
```

Kết quả kiểm thử:

```text
needs_tax=True, needs_compliance=True
call_tax_specialist Done
call_compliance_specialist Done
aggregate Done
```

Kết luận:

Stage 4 pass vì Tax Specialist và Compliance Specialist đã được gọi, chạy song song bằng LangGraph Send API, sau đó kết quả được aggregate thành final answer.

---

## Stage 5 - Distributed A2A Multi-Agent System

Đã kiểm thử Stage 5 với kiến trúc distributed multi-agent system.

Các services được chạy độc lập:

```text
Registry:         http://localhost:10000
Customer Agent:   http://localhost:10100
Law Agent:        http://localhost:10101
Tax Agent:        http://localhost:10102
Compliance Agent: http://localhost:10103
```

Command chạy toàn bộ hệ thống:

```bash
./start_all.sh
```

Command gửi request end-to-end:

```bash
uv run python test_client.py
```

Kiến trúc Stage 5:

```text
User
→ Customer Agent
→ Registry discovery
→ Law Agent
→ Routing
→ Tax Agent + Compliance Agent
→ Aggregation
→ Customer Agent
→ User
```

Kết luận:

Stage 5 pass vì các agents chạy dưới dạng services riêng biệt và giao tiếp thông qua A2A Protocol.

---

## Stage 5.1 - Trace Flow

Đã kiểm thử trace propagation qua toàn bộ distributed A2A workflow.

Các thông tin trace được truyền qua các agents:

- `trace_id`
- `context_id`
- `delegation_depth`

Log quan sát được:

```text
CustomerAgent executing ... trace=... depth=0
LawAgent executing ... trace=... depth=1
TaxAgent executing ... trace=... depth=2
ComplianceAgent executing ... trace=... depth=2
```

Trace flow:

```text
User
→ Customer Agent, depth=0
→ Registry discovery for legal_question
→ Law Agent, depth=1
→ Law Agent routing
→ Registry discovery for tax_question
→ Tax Agent, depth=2
→ Registry discovery for compliance_question
→ Compliance Agent, depth=2
→ Law Agent aggregation
→ Customer Agent final response
→ User
```

Kết luận:

Stage 5.1 pass vì cùng một `trace_id` và `context_id` được propagate qua Customer Agent, Law Agent, Tax Agent và Compliance Agent.

---

## Stage 5.2 - Dynamic Discovery và Failure Handling

Đã kiểm thử dynamic discovery và failure handling bằng cách tắt Tax Agent trên port `10102`.

Command tìm process của Tax Agent:

```bash
netstat -ano | grep ":10102"
```

Command tắt Tax Agent:

```bash
taskkill //PID <PID> //F
```

Sau khi tắt Tax Agent, chạy lại client:

```bash
uv run python test_client.py
```

Log quan sát được:

```text
law_agent ERROR call_tax failed: All connection attempts failed
httpx.ConnectError: All connection attempts failed
```

Tuy Tax Agent bị tắt, hệ thống vẫn không crash. Compliance Agent vẫn hoàn thành:

```text
Compliance Agent returned 763 chars
```

Customer Agent vẫn trả final response cho user.

Kết luận:

Stage 5.2 pass vì hệ thống distributed A2A có thể chịu lỗi khi một specialist agent không khả dụng. Law Agent ghi nhận lỗi Tax Agent nhưng vẫn tiếp tục workflow với partial results.

---

## Stage 5.3 - Modify Tax Agent Behavior

Đã sửa behavior của Tax Agent bằng cách cập nhật prompt để câu trả lời ngắn gọn hơn.

Instruction được thêm vào Tax Agent prompt:

```text
Keep the answer concise. Maximum 100 words. Use bullet points. Avoid repetition.
```

Mục tiêu:

- Giảm verbosity.
- Giúp Tax Agent trả lời ngắn gọn hơn.
- Hỗ trợ latency optimization.
- Giữ nguyên số lượng LLM calls và kiến trúc A2A.

Kết luận:

Stage 5.3 pass vì Tax Agent behavior đã được chỉnh sửa và output sau khi rerun ngắn gọn hơn.

---

## Bonus - Latency Optimization

Đã thêm đo latency vào `test_client.py`.

Baseline latency:

```text
76.38 seconds
```

Optimized latency tốt nhất:

```text
27.19 seconds
```

Mức cải thiện:

```text
49.19 seconds faster
Approximately 64.4% reduction
```

Một số lần rerun sau optimization cho kết quả khoảng:

```text
21-30 seconds
```

Quan trọng: số lượng LLM calls không bị giảm. Full A2A workflow vẫn được giữ nguyên:

```text
Customer Agent
→ Law Agent
→ Routing
→ Tax Agent + Compliance Agent
→ Aggregation
```

Các optimization đã thực hiện:

- Dùng model OpenRouter nhanh hơn.
- Giảm temperature.
- Thêm `max_tokens` limit.
- Rút gọn prompt của specialist agents.
- Làm Tax Agent và Compliance Agent trả lời concise hơn.

Kết luận:

Bonus pass vì latency giảm từ 76.38s xuống 27.19s, tương đương giảm khoảng 64.4%, trong khi vẫn giữ nguyên full multi-agent workflow.

---

## 3. Các file đã chỉnh sửa

```text
common/llm.py
compliance_agent/graph.py
exercises/exercise_2_tools.py
exercises/exercise_4_multiagent.py
law_agent/graph.py
stages/stage_3_single_agent/main.py
start_all.sh
tax_agent/graph.py
test_client.py
SUBMISSION.md
```

Ý nghĩa các thay đổi:

- `common/llm.py`: cấu hình LLM để tối ưu latency.
- `compliance_agent/graph.py`: rút gọn prompt/output.
- `tax_agent/graph.py`: sửa Tax Agent behavior theo yêu cầu Stage 5.3.
- `law_agent/graph.py`: cải thiện aggregation và xử lý warning/fallback.
- `test_client.py`: thêm đo latency.
- `start_all.sh`: sửa command để chạy đúng bằng `uv run` trên môi trường local.
- `exercises/exercise_2_tools.py`: hoàn thành Exercise 2.
- `stages/stage_3_single_agent/main.py`: thêm `search_case_law`.
- `exercises/exercise_4_multiagent.py`: thêm Privacy Agent và conditional routing.
- `SUBMISSION.md`: báo cáo nộp bài.

---

## 4. Final Verification Commands

Các command đã dùng để kiểm thử:

```bash
uv run python exercises/exercise_2_tools.py
uv run python stages/stage_3_single_agent/main.py
uv run python exercises/exercise_4_multiagent.py
uv run python stages/stage_4_milti_agent/main.py
./start_all.sh
uv run python test_client.py
```

Kết quả tổng hợp:

```text
Exercise 2: pass
Stage 3 + search_case_law: pass
Exercise 4 + Privacy Agent: pass
Stage 4 multi-agent: pass
Stage 5 distributed A2A: pass
Stage 5 trace flow: pass
Stage 5 dynamic discovery/failure handling: pass
Stage 5 Tax Agent behavior modification: pass
Bonus latency optimization: pass
```

---

## 5. Notes

- `.env` không được commit.
- Các deprecation warnings từ LangGraph và A2A SDK không làm ảnh hưởng đến execution.
- Folder `stage_4_milti_agent` được giữ nguyên theo tên trong repo gốc.
- Project chạy bằng `uv`.
- Các thuật ngữ chuyên ngành như Agent, Tool, Registry, A2A Protocol, LangGraph, Routing, Aggregation, Trace Flow, Dynamic Discovery, Failure Handling được giữ bằng tiếng Anh để đúng với nội dung kỹ thuật của lab.

---

## 6. Kết luận

Bài làm đã hoàn thành đầy đủ các yêu cầu chính của Day 9 Lab:

- Xây dựng và kiểm thử tool-using agent.
- Mở rộng ReAct agent với case law search tool.
- Xây dựng in-process multi-agent system.
- Thêm Privacy Agent và conditional routing.
- Chạy distributed A2A multi-agent system.
- Kiểm thử trace propagation.
- Kiểm thử dynamic discovery và failure handling.
- Chỉnh sửa Tax Agent behavior.
- Đo và tối ưu latency.

Hệ thống cuối cùng thể hiện đầy đủ kiến trúc multi-agent có routing, specialist agents, service discovery, trace propagation, failure tolerance và latency optimization.