import re

import setuptools
from setuptools.command.build_ext import build_ext


class SourceModifyingCompilation(build_ext):
    def run(self):
        self.modify_sources()
        build_ext.run(self)

    def modify_sources(self):
        for ext in self.extensions:
            for source_file in ext.sources:
                if source_file.endswith(".c") or source_file.endswith(".cpp"):
                    self.transform_c_code(source_file)


    def transform_c_code(self, filename, str_max_length=16000):
        print(f"transforming {filename}")
        #Splits long strings in a C/C++ file to avoid C2026 error.
        with open(filename, 'r') as file:
            content = file.read()

        def replace_string(match):
            string = match.group(0)
            if len(string) > str_max_length:
                parts = [string[i:i + str_max_length] for i in range(0, len(string), str_max_length)]
                parts[0] = parts[0].replace('"', "")
                parts[-1] = parts[-1].replace('"', "")
                return '"' + '""'.join(parts) + '"'
            return string

        pattern = r'"[^"\\]*(\\.[^"\\]*)*"'
        modified_content = re.sub(pattern, replace_string, content)

        with open(filename, 'w') as file:
            file.write(modified_content)

setuptools.setup(
    name="vma",
    version="1.0.0",
    description="Vulkan-Project-VMA",
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["vma/vma_build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
    cmdclass={"build_ext":SourceModifyingCompilation}
)
