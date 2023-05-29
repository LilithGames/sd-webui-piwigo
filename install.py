import launch

# TODO: add pip dependency if need extra module only on extension

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requests")

if not launch.is_installed("httpx"):
    launch.run_pip("install httpx", "httpx")

if not launch.is_installed("aiofiles"):
    launch.run_pip("install aiofiles", "aiofiles")
