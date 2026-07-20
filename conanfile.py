from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout
from pathlib import Path
import re
import yaml


class SilConan(ConanFile):
    name = "adas-sil"
    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"

    # Accepted for CLI/package_id uniformity across every component (plan.md
    # item 10, docs/build_conanfile_commonization_plan.md §2.3) - currently
    # unused for any real branching, same status quo perception-core's own
    # project option already has. Real requires: wiring driven by project
    # (adas-df/adas-vdy) is plan.md item 11, not this item.
    options = {
        "project": ["ANY"],
    }

    default_options = {
        "project": "base",
        "protobuf/*:shared": False,
        "protobuf/*:with_zlib": False,
    }

    def _build_conf(self):
        conf_path = Path(self.recipe_folder) / "conf" / "build.yml"
        conf = yaml.safe_load(conf_path.read_text(encoding="utf-8"))
        return conf["variants"][str(self.options.project)]

    def requirements(self):
        for ref in self._build_conf().get("requires", []):
            self.requires(ref)

    def build_requirements(self):
        for ref in self._build_conf().get("tool_requires", []):
            self.tool_requires(ref)

    def layout(self):
        # plan.md item 11, docs/sil_dependency_wiring_plan.md - same
        # conditional template copied into every component's conanfile.py
        # (item 10's own philosophy), branching on this file's own
        # layout_kind and Conan's own self.package_type (package_kind was
        # removed from conf/build.yml entirely,
        # docs/build_regression_tests.md §5). A no-op for this component
        # (package_type "application" is never find_package()'d by another
        # component) - kept for template consistency, not because anything
        # here reads it yet.
        conf_path = Path(self.recipe_folder) / "conf" / "build.yml"
        conf = yaml.safe_load(conf_path.read_text(encoding="utf-8"))
        layout_kind = conf.get("layout_kind", "output_folder")

        if layout_kind == "cmake_layout":
            cmake_layout(self)
            self.cpp.source.includedirs = ["cpp"]
            self.cpp.build.includedirs = ["generated"]
        elif self.package_type in ("shared-library", "static-library"):
            comp = self.name.replace("adas-", "")
            platform = conf["variants"][str(self.options.project)]["sil"]["platforms"][0]["build"]
            build_type = str(self.settings.build_type) if self.settings.get_safe("build_type") else "Release"
            self.cpp.source.includedirs = [f"src/platform/{comp}_sil"]
            self.cpp.build.libdirs = [f"build-sil-{platform}/src/platform/{comp}_sil/{build_type}"]
            self.cpp.build.bindirs = [f"build-sil-{platform}/src/platform/{comp}_sil/{build_type}"]

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
