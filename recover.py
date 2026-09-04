import json

log_file = "/Users/vivek/.gemini/antigravity-ide/brain/71d42b51-5e25-4db8-94a7-530ece43b1ab/.system_generated/logs/transcript_full.jsonl"
with open(log_file, "r") as f:
    lines = f.readlines()

for line in lines:
    try:
        data = json.loads(line)
        if "tool_calls" in data:
            for call in data["tool_calls"]:
                if call["name"] in ["write_to_file", "replace_file_content"]:
                    args = call["args"]
                    if "TargetFile" in args and ("run_ui_tests.py" in args["TargetFile"] or "image_utils.py" in args["TargetFile"]):
                        print(f"FOUND write to {args['TargetFile']}")
                        if "CodeContent" in args:
                            print(args["CodeContent"][:200])
                        elif "ReplacementContent" in args:
                            print(args["ReplacementContent"][:200])
    except Exception as e:
        pass
