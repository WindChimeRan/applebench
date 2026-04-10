#!/usr/bin/env python3
"""Compose agent benchmark prompts from BFCL V3, Hermes Agent Traces, and ClawsBench.

Produces prompts/agent_benchmark_prompts.json with 100 multi-turn agentic prompts
in the same format as prompts/benchmark_prompts.json.
"""

import json
import random
import re
from pathlib import Path

random.seed(42)

OUTPUT = Path(__file__).parent.parent / "prompts" / "agent_benchmark_prompts.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token)."""
    return len(text) // 4


def msgs_token_count(messages: list[dict]) -> int:
    total = 0
    for m in messages:
        if m.get("content"):
            total += estimate_tokens(str(m["content"]))
        if m.get("tool_calls"):
            total += estimate_tokens(json.dumps(m["tool_calls"]))
    return total


def size_bucket(tok: int) -> str:
    if tok < 200:
        return "short"
    elif tok < 800:
        return "medium"
    elif tok < 2000:
        return "long"
    else:
        return "vlong"


# ---------------------------------------------------------------------------
# 1. BFCL V3 Multi-Turn (35 samples)
# ---------------------------------------------------------------------------

def parse_func_call(call_str: str) -> dict:
    """Parse 'func_name(arg1=val1, arg2=val2)' into OpenAI tool_call format."""
    m = re.match(r"(\w+)\((.*)\)$", call_str, re.DOTALL)
    if not m:
        return {"name": call_str, "arguments": "{}"}
    name = m.group(1)
    args_str = m.group(2).strip()
    # Parse keyword arguments
    args = {}
    if args_str:
        # Simple parsing: split on comma, then key=value
        # Handle nested quotes and brackets carefully
        try:
            # Use eval to parse Python-style kwargs safely
            args = eval(f"dict({args_str})", {"__builtins__": {}})
        except Exception:
            args = {"raw": args_str}
    return {"name": name, "arguments": json.dumps(args)}


def load_bfcl_tools() -> dict:
    """Load BFCL tool definitions from downloaded files."""
    tools_dir = Path("/tmp/bfcl_tools")
    all_tools = {}
    for f in sorted(tools_dir.glob("*.json")):
        class_name = f.stem
        with open(f) as fh:
            content = fh.read().strip()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = [json.loads(line) for line in content.split("\n") if line.strip()]
        if isinstance(data, list):
            all_tools[class_name] = data
    return all_tools


# Map BFCL class names to tool doc file names
BFCL_CLASS_MAP = {
    "GorillaFileSystem": "gorilla_file_system",
    "MathAPI": "math_api",
    "MessageAPI": "message_api",
    "PostingAPI": "posting_api",
    "TicketAPI": "ticket_api",
    "TradingBot": "trading_bot",
    "TravelAPI": "travel_booking",
    "VehicleControlAPI": "vehicle_control",
    "TwitterAPI": "posting_api",
}


def build_bfcl_prompts() -> list[dict]:
    """Build multi-turn prompts from BFCL V3 multi-turn base."""
    with open("/tmp/bfcl_multi_turn.json") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    all_tools = load_bfcl_tools()
    prompts = []

    for entry in entries:
        questions = entry["question"]  # list of turns, each is list of msgs
        involved = entry.get("involved_classes", [])
        path = entry.get("path", [])

        # Collect tool definitions for this entry
        tool_defs = []
        for cls in involved:
            file_key = BFCL_CLASS_MAP.get(cls, cls.lower())
            if file_key in all_tools:
                tool_defs.extend(all_tools[file_key])

        # Build system message with tool definitions
        tool_desc = json.dumps(tool_defs, indent=2) if tool_defs else "No tools available."
        system_msg = (
            "You are a helpful assistant with access to the following tools. "
            "Call them as needed to fulfill user requests.\n\n"
            f"Available tools:\n{tool_desc}"
        )

        # Build multi-turn conversation
        messages = [{"role": "system", "content": system_msg}]

        # Flatten path into per-turn groups
        turn_calls = []
        call_idx = 0
        for turn_i, q_turn in enumerate(questions):
            # Estimate how many calls belong to this turn
            # (BFCL path is a flat list of all calls across all turns)
            remaining_turns = len(questions) - turn_i
            calls_per_turn = max(1, (len(path) - call_idx) // remaining_turns)
            turn_calls.append(path[call_idx : call_idx + calls_per_turn])
            call_idx += calls_per_turn

        for turn_i, q_turn in enumerate(questions):
            # Add user message(s) for this turn
            for msg in q_turn:
                messages.append({"role": "user", "content": msg["content"]})

            # For all turns except the last, add simulated assistant + tool response
            if turn_i < len(questions) - 1:
                calls = turn_calls[turn_i] if turn_i < len(turn_calls) else []
                if calls:
                    tool_calls = []
                    for ci, call_str in enumerate(calls):
                        parsed = parse_func_call(call_str)
                        tool_calls.append({
                            "id": f"call_{turn_i}_{ci}",
                            "type": "function",
                            "function": parsed,
                        })
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_calls,
                    })
                    # Add tool results
                    for tc in tool_calls:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps({
                                "status": "success",
                                "result": f"Operation '{tc['function']['name']}' completed successfully.",
                            }),
                        })
                else:
                    messages.append({
                        "role": "assistant",
                        "content": "Done. What would you like to do next?",
                    })

        tok = msgs_token_count(messages)
        num_turns = len(questions)
        prompts.append({
            "name": f"bfcl_{entry['id']}",
            "description": f"BFCL multi-turn: {num_turns} turns, ~{tok} input tokens, tools: {', '.join(involved)}",
            "messages": messages,
            "max_tokens": 256,
            "source": "bfcl_v3",
        })

    return prompts


# ---------------------------------------------------------------------------
# 2. Hermes Agent Reasoning Traces (35 samples)
# ---------------------------------------------------------------------------

HERMES_ROLE_MAP = {"system": "system", "human": "user", "gpt": "assistant", "tool": "tool"}


def clean_hermes_content(content: str, role: str) -> str:
    """Clean Hermes content: remove <think> blocks for cleaner prompts."""
    if role == "assistant":
        # Remove <think>...</think> blocks to reduce noise
        content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL)
    return content.strip()


def extract_tool_calls_from_hermes(content: str) -> tuple[list[dict], str]:
    """Extract <tool_call> XML from Hermes assistant content."""
    tool_calls = []
    remaining = content

    pattern = r"<tool_call>\s*(\{.*?\})\s*</tool_call>"
    matches = list(re.finditer(pattern, content, re.DOTALL))
    for i, m in enumerate(matches):
        try:
            tc_data = json.loads(m.group(1))
            tool_calls.append({
                "id": f"hermes_call_{i}",
                "type": "function",
                "function": {
                    "name": tc_data.get("name", "unknown"),
                    "arguments": json.dumps(tc_data.get("arguments", {})),
                },
            })
        except json.JSONDecodeError:
            pass
        remaining = remaining.replace(m.group(0), "")

    return tool_calls, remaining.strip()


def extract_tool_response(content: str) -> str:
    """Extract content from <tool_response>...</tool_response>."""
    m = re.search(r"<tool_response>\s*(.*?)\s*</tool_response>", content, re.DOTALL)
    if m:
        return m.group(1)
    return content


def build_hermes_prompts() -> list[dict]:
    """Build prompts from Hermes agent reasoning traces."""
    from datasets import load_dataset

    ds = load_dataset("lambda/hermes-agent-reasoning-traces", "kimi", split="train")

    prompts = []
    tc_id_counter = 0
    for row in ds:
        convs = row["conversations"]
        n_msgs = len(convs)
        # Filter: 6-24 messages, reasonable length
        if n_msgs < 6 or n_msgs > 24:
            continue

        # ShareGPT format uses 'from'/'value' keys, not 'role'/'content'
        roles_raw = [c.get("from", c.get("role", "?")) for c in convs]
        # Must have at least one tool turn to be truly agentic
        if "tool" not in roles_raw:
            continue

        # Convert to OpenAI format
        messages = []
        tc_id_counter = 0
        for conv in convs:
            from_role = conv.get("from", conv.get("role", "user"))
            role = HERMES_ROLE_MAP.get(from_role, from_role)
            content = conv.get("value", conv.get("content", ""))

            if role == "system":
                # Truncate overly long system prompts but keep tool definitions
                if len(content) > 8000:
                    content = content[:8000] + "\n...[truncated]"
                messages.append({"role": "system", "content": content})

            elif role == "user":
                messages.append({"role": "user", "content": content})

            elif role == "assistant":
                cleaned = clean_hermes_content(content, "assistant")
                tool_calls, remaining_text = extract_tool_calls_from_hermes(cleaned)
                if tool_calls:
                    # Assign unique IDs
                    for tc in tool_calls:
                        tc["id"] = f"hermes_call_{tc_id_counter}"
                        tc_id_counter += 1
                    msg = {
                        "role": "assistant",
                        "content": remaining_text if remaining_text else None,
                        "tool_calls": tool_calls,
                    }
                    messages.append(msg)
                elif remaining_text:
                    messages.append({"role": "assistant", "content": remaining_text})

            elif role == "tool":
                tool_content = extract_tool_response(content)
                # Find the last assistant tool_call to get the ID
                tool_call_id = "unknown"
                for prev in reversed(messages):
                    if prev.get("tool_calls"):
                        used_ids = {m.get("tool_call_id") for m in messages if m.get("role") == "tool"}
                        for tc in prev["tool_calls"]:
                            if tc["id"] not in used_ids:
                                tool_call_id = tc["id"]
                                break
                        break
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_content[:2000],
                })

        if len(messages) < 4:
            continue

        # Must have actual tool calls in the converted messages
        if not any(m.get("tool_calls") for m in messages):
            continue

        # Remove the last assistant message so the model generates it
        if messages[-1]["role"] == "assistant":
            messages = messages[:-1]

        tok = msgs_token_count(messages)
        # Skip if too short or too long
        if tok < 100 or tok > 6000:
            continue

        n_tool_calls = sum(1 for m in messages if m.get("tool_calls"))
        prompts.append({
            "name": f"hermes_{row['id']}",
            "description": (
                f"Hermes agent trace: {row['category']}/{row['subcategory']}, "
                f"{len(messages)} msgs, ~{tok} input tokens, {n_tool_calls} tool calls"
            ),
            "messages": messages,
            "max_tokens": 256,
            "source": "hermes",
        })

    return prompts


# ---------------------------------------------------------------------------
# 3. ClawsBench (30 samples)
# ---------------------------------------------------------------------------

CLAWSBENCH_SERVICES = {
    "gmail": "Gmail API: search_emails, read_email, send_email, reply_email, forward_email, delete_email, archive_email, label_email, list_labels",
    "slack": "Slack API: list_channels, read_channel, post_message, reply_thread, list_dms, read_dm, send_dm",
    "calendar": "Google Calendar API: list_events, create_event, update_event, delete_event, get_event",
    "docs": "Google Docs API: create_doc, read_doc, update_doc, list_docs, share_doc",
    "drive": "Google Drive API: list_files, upload_file, download_file, move_file, delete_file, share_file",
}


def build_clawsbench_prompts() -> list[dict]:
    """Build prompts from ClawsBench agent traces."""
    with open("/tmp/clawsbench_data.jsonl") as f:
        data = [json.loads(line) for line in f if line.strip()]

    with open("/tmp/clawsbench_tasks.json") as f:
        task_meta = json.load(f)

    prompts = []
    seen_tasks = set()

    for row in data:
        task_name = row["task_name"]
        # One trace per task to keep variety
        if task_name in seen_tasks:
            continue

        meta = task_meta.get(task_name, {})
        instruction = meta.get("instruction_preview", "")
        if not instruction:
            continue

        services = meta.get("services", [])
        n_steps = row["n_steps"]
        if n_steps < 3 or n_steps > 20:
            continue

        traces = row["traces"]
        if isinstance(traces, str):
            traces = json.loads(traces)

        # Build system message
        svc_desc = "\n".join(
            f"- {CLAWSBENCH_SERVICES.get(s, s)}" for s in services
        )
        system_msg = (
            "You are a productivity assistant. You have access to the following services:\n"
            f"{svc_desc}\n\n"
            "Execute the user's request by calling the appropriate tools."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": instruction},
        ]

        # Convert trace steps to messages (use up to 8 steps to keep size manageable)
        for step in traces[:8]:
            tool_calls_raw = step.get("tool_calls", [])
            obs = step.get("observation", {})
            msg_text = step.get("message", "").strip()

            if tool_calls_raw:
                tool_calls = []
                for ci, tc in enumerate(tool_calls_raw):
                    fn_name = tc.get("function_name", "tool")
                    args = tc.get("arguments", {})
                    tool_calls.append({
                        "id": f"claw_{step['step_id']}_{ci}",
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": json.dumps(args) if isinstance(args, dict) else str(args),
                        },
                    })
                messages.append({
                    "role": "assistant",
                    "content": msg_text if msg_text else None,
                    "tool_calls": tool_calls,
                })

                # Add tool results from observation
                if obs and obs.get("results"):
                    for ri, result in enumerate(obs["results"]):
                        tc_id = tool_calls[ri]["id"] if ri < len(tool_calls) else f"claw_{step['step_id']}_obs"
                        result_content = result.get("content", "")
                        if len(result_content) > 1500:
                            result_content = result_content[:1500] + "...[truncated]"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc_id,
                            "content": result_content,
                        })
            elif msg_text:
                messages.append({"role": "assistant", "content": msg_text})

        # Remove last assistant message so model generates it
        if messages[-1]["role"] == "assistant":
            messages = messages[:-1]

        tok = msgs_token_count(messages)
        if tok < 100 or tok > 6000:
            continue

        seen_tasks.add(task_name)
        tags = ", ".join(meta.get("tags", []))
        prompts.append({
            "name": f"claws_{task_name}",
            "description": (
                f"ClawsBench: {task_name}, services: {', '.join(services)}, "
                f"~{tok} input tokens, {n_steps} agent steps"
            ),
            "messages": messages,
            "max_tokens": 256,
            "source": "clawsbench",
        })

    return prompts


# ---------------------------------------------------------------------------
# Main: Compose and sample
# ---------------------------------------------------------------------------

def main():
    print("Building BFCL V3 multi-turn prompts...")
    bfcl = build_bfcl_prompts()
    print(f"  -> {len(bfcl)} candidates")

    print("Building Hermes agent trace prompts...")
    hermes = build_hermes_prompts()
    print(f"  -> {len(hermes)} candidates")

    print("Building ClawsBench prompts...")
    claws = build_clawsbench_prompts()
    print(f"  -> {len(claws)} candidates")

    # Sample: 35 BFCL, 35 Hermes, 30 ClawsBench = 100 total
    n_bfcl = min(35, len(bfcl))
    n_claws = min(30, len(claws))
    n_hermes = min(100 - n_bfcl - n_claws, len(hermes))

    sampled_bfcl = random.sample(bfcl, n_bfcl) if len(bfcl) > n_bfcl else bfcl
    sampled_hermes = random.sample(hermes, n_hermes) if len(hermes) > n_hermes else hermes
    sampled_claws = random.sample(claws, n_claws) if len(claws) > n_claws else claws

    all_prompts = sampled_bfcl + sampled_hermes + sampled_claws
    random.shuffle(all_prompts)

    # Re-index with sequential names
    for i, p in enumerate(all_prompts):
        tok = msgs_token_count(p["messages"])
        n_msgs = len(p["messages"])
        bucket = size_bucket(tok)
        p["name"] = f"a{i:03d}_{bucket}_{p['source']}"

    # Remove internal 'source' field
    for p in all_prompts:
        del p["source"]

    # Stats
    print(f"\nFinal dataset: {len(all_prompts)} prompts")
    print(f"  BFCL: {n_bfcl}, Hermes: {n_hermes}, ClawsBench: {n_claws}")
    for p in all_prompts[:3]:
        print(f"  {p['name']}: {p['description'][:80]}...")

    # Token distribution
    tokens = [msgs_token_count(p["messages"]) for p in all_prompts]
    print(f"\nToken stats: min={min(tokens)}, max={max(tokens)}, "
          f"avg={sum(tokens)//len(tokens)}, median={sorted(tokens)[len(tokens)//2]}")

    msg_counts = [len(p["messages"]) for p in all_prompts]
    print(f"Message counts: min={min(msg_counts)}, max={max(msg_counts)}, "
          f"avg={sum(msg_counts)//len(msg_counts)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(all_prompts, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {OUTPUT}")


if __name__ == "__main__":
    main()
