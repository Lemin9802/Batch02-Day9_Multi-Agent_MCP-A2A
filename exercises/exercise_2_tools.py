"""Bài Tập 2: Thêm Tools và Knowledge Base

"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from common.llm import get_llm

# Knowledge base
LEGAL_KNOWLEDGE = [
    {
        "id": "ucc_breach",
        "keywords": ["breach", "contract", "remedies", "damages", "ucc"],
        "text": (
            "Under the Uniform Commercial Code (UCC) Article 2, remedies for breach of contract "
            "include: (1) expectation damages; (2) consequential damages; (3) specific performance; "
            "(4) cover damages. Statute of limitations is typically 4 years (UCC § 2-725)."
        ),
    },

    {
        "id": "contract_limitation",
        "keywords": ["thời hiệu", "khởi kiện", "vi phạm", "hợp đồng"],
        "text": (
            "Thời hiệu khởi kiện vụ vi phạm hợp đồng là 3 năm kể từ ngày người có quyền "
            "yêu cầu biết hoặc phải biết quyền và lợi ích hợp pháp của mình bị xâm phạm. "
            "Đây là thời hiệu thường áp dụng cho tranh chấp hợp đồng dân sự/thương mại."
        )
    }
]


@tool
def search_legal_knowledge(query: str) -> str:
    """Search legal knowledge base by keyword.

    Args:
        query: Legal search query.
    """
    q = query.lower()
    results = []

    for item in LEGAL_KNOWLEDGE:
        item_id = item.get("id", "").lower()
        keywords = [kw.lower() for kw in item.get("keywords", [])]
        text = item.get("text", "")

        if item_id in q or any(keyword in q for keyword in keywords):
            results.append(text)

    if results:
        return "\n\n".join(results)

    return "Không tìm thấy thông tin liên quan."

@tool
def check_statute_of_limitations(case_type: str) -> str:
    """Check statute of limitations for a legal case type.

    Args:
        case_type: Type of legal case, such as contract, tort, or tax.
    """
    case_type_lower = case_type.lower()

    if (
        "contract" in case_type_lower
        or "hợp đồng" in case_type_lower
        or "hop dong" in case_type_lower
        or "vi phạm" in case_type_lower
        or "vi pham" in case_type_lower
    ):
        return (
            "Thời hiệu khởi kiện vụ vi phạm hợp đồng là 3 năm kể từ ngày người có quyền "
            "yêu cầu biết hoặc phải biết quyền và lợi ích hợp pháp của mình bị xâm phạm."
        )

    return "Chưa có thông tin thời hiệu cho loại vụ việc này."


async def main():
    load_dotenv()
    llm = get_llm()
    

    tools = [search_legal_knowledge, check_statute_of_limitations]
    llm_with_tools = llm.bind_tools(tools)
    
    question = "Thời hiệu khởi kiện vụ vi phạm hợp đồng là bao lâu?"
    
    messages = [
        SystemMessage(content="Bạn là chuyên gia pháp lý. Sử dụng tools để tra cứu thông tin."),
        HumanMessage(content=question),
    ]
    
    print(f"Câu hỏi: {question}\n")
    
    # First LLM call - decide which tools to use
    response = await llm_with_tools.ainvoke(messages)
    messages.append(response)
    
    # Execute tools if requested
    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"🔧 Gọi tool: {tool_call['name']}")
            tool_result = None

            if tool_call["name"] == "search_legal_knowledge":
                tool_result = search_legal_knowledge.invoke(tool_call["args"])
            elif tool_call["name"] == "check_statute_of_limitations":
                tool_result = check_statute_of_limitations.invoke(tool_call["args"])
            else:
                tool_result = f"Unknown tool: {tool_call['name']}"

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        # Second LLM call - synthesize final answer
        # Use plain llm here to avoid another round of tool calls.
        final_response = await llm.ainvoke(messages)

        if final_response.content:
            print(f"\n✅ Kết quả:\n{final_response.content}")
        else:
            print("\n✅ Kết quả từ tools:")
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    print(msg.content)
    else:
        print("\nKhông có tool nào được gọi.")
        print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
