from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain
from pathlib import Path
import re


class SilConan(ConanFile):
    name = "adas-sil"
    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"
    requires = ("protobuf/3.21.12", "adas-interfaces/1.0.0")
    tool_requires = ("protobuf/3.21.12",)

    default_options = {
        "protobuf/*:shared": False,
        "protobuf/*:with_zlib": False,
    }

    def set_version(self):
        cmakelists = Path(self.recipe_folder) / "CMakeLists.txt"
        content = cmakelists.read_text(encoding="utf-8")
        match = re.search(r"project\(\s*adas-sil\s+VERSION\s+([0-9]+\.[0-9]+\.[0-9]+)", content, re.IGNORECASE)
        if not match:
            raise RuntimeError("Could not extract VERSION from CMakeLists.txt")
        self.version = match.group(1)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.build_context_activated = ["protobuf"]
        deps.build_context_suffix = {"protobuf": "_BUILD"}
        deps.generate()
