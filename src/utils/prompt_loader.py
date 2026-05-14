try:
    from utils.config_handler import prompts_conf
    from utils.path_tool import get_abs_path
    from utils.logger_handler import logger
except ModuleNotFoundError:
    from config_handler import prompts_conf
    from path_tool import get_abs_path
    from logger_handler import logger


def _load_prompt(config_key: str, loader_name: str) -> str:
    try:
        prompt_path = get_abs_path(prompts_conf[config_key])
    except KeyError as e:
        logger.error(f"[{loader_name}] Missing config key in config/prompts.yml: {config_key}")
        raise e

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"[{loader_name}] Prompt file does not exist: {prompt_path}")
        raise e
    except OSError as e:
        logger.error(f"[{loader_name}] Failed to read prompt file {prompt_path}: {e}")
        raise e


def load_system_prompts():
    return _load_prompt("main_prompt_path", "load_system_prompts")


def load_rag_prompts():
    return _load_prompt("rag_summarize_prompt_path", "load_rag_prompts")


def load_report_prompts():
    return _load_prompt("report_prompt_path", "load_report_prompts")


if __name__ == "__main__":
    print(load_report_prompts())
