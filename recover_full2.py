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
                    if "TargetFile" in args and "run_ui_tests.py" in args["TargetFile"]:
                        if "CodeContent" in args and "calculate_pixel_diff" in args["CodeContent"] and "subprocess" in args["CodeContent"]:
                            with open("recovered_run_ui_tests_diff.py", "w") as out:
                                out.write(args["CodeContent"])
                        elif "ReplacementContent" in args and "calculate_pixel_diff" in args["ReplacementContent"]:
                            with open("recovered_run_ui_tests_diff.py", "w") as out:
                                out.write(args["ReplacementContent"])
    except Exception as e:
        pass
