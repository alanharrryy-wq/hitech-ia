def module_info() -> dict:
    return {
        "module_name": "{{MODULE_NAME}}",
        "summary": "{{SUMMARY}}",
        "features": {{FEATURES}}
    }

def main() -> None:
    info = module_info()
    print(f"{info['module_name']}: {info['summary']}")

if __name__ == "__main__":
    main()
