import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import uuid
import argparse
from argparse import RawTextHelpFormatter


def replace_words(text, words_to_replace):
    for old, new in words_to_replace.items():
        text = text.replace(old, new)
        text = text.replace(old.upper(), new.upper())
    return text


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="Duplicates a Power Platform solution by cloning all its components and replacing specific domain words in all files.\nIN: the path to the zip file of the solution ti duplicate.\nOUT: the duplicated solution as a new zip file.",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("zip_path", help="Path to the solution zip file")
    parser.add_argument(
        "-rw",
        "--replace_words",
        help='Comma separated list of word couples to replace. The couples are separated by "|".\nEg Madrid|Amsterdam,First|Second',
    )

    args = parser.parse_args()

    couples = args.replace_words = args.replace_words.split(",")
    words_to_replace = {}
    for couple in couples:
        old, new = couple.split("|")
        words_to_replace[old] = new

    return args.zip_path, words_to_replace


def extract_zip_file(path):
    # create temp folder for extracted files
    os.mkdir(f"{os.path.dirname(path)}/tmp")

    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(path=f"{os.path.dirname(path)}/tmp")

    return f"{os.path.dirname(path)}/tmp"


def amend_file(path, words, components=None, connections=None, variables=None):
    with open(path, "r", encoding="utf8") as file:
        data = file.read()
        if variables is not None:
            data = replace_words(data, variables)
        if connections is not None:
            data = replace_words(data, connections)
        if components is not None:
            data = replace_words(data, components)
        data = replace_words(data, words)
    with open(path, "w", encoding="utf8") as file:
        file.write(data)
        file.seek(0)


def read_and_amend_solution_file(path, words_to_replace):
    solution_file_path = f"{path}/solution.xml"
    tree = ET.parse(solution_file_path)
    solution_root = tree.getroot().find("SolutionManifest")
    solution_root.find("UniqueName").text = replace_words(
        solution_root.find("UniqueName").text, words_to_replace
    )
    solution_root.find("Version").text = "1.0.0.0"
    solution_root.find("Managed").text = "0"

    components_guid_dictionary = {}
    for component in solution_root.find("RootComponents").findall("RootComponent"):
        components_guid_dictionary[component.get("id")[1:-1]] = str(uuid.uuid4())

    tree.write(solution_file_path)

    amend_file(solution_file_path, words_to_replace, components_guid_dictionary)

    return components_guid_dictionary


def read_and_amend_customizations_file(path, words, components):
    customizations_file_path = f"{path}/customizations.xml"
    connection_references = {}

    tree = ET.parse(customizations_file_path)
    root = tree.getroot()
    for workflow in root.find("Workflows").findall("Workflow"):
        workflow.find("IntroducedVersion").text = "1.0.0.0"

    for connection_reference in root.find("connectionreferences").findall(
        "connectionreference"
    ):
        logical_name = connection_reference.get("connectionreferencelogicalname")
        new_logical_name = logical_name[0:-5] + str(uuid.uuid4())[-5:]
        connection_references[logical_name] = new_logical_name
        connection_reference.set("connectionreferencelogicalname", new_logical_name)

    tree.write(customizations_file_path)

    amend_file(customizations_file_path, words, components)

    return connection_references


def read_and_amend_environmental_variables(path, words, components):
    variable_schema_name = {}
    # for each folder in the path
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            new_dir_path = os.path.join(root, replace_words(dir, words))
            if dir_path == new_dir_path:
                shutil.rmtree(dir_path)
                continue
            # amend files
            for root_dir, subdirs, subfiles in os.walk(dir_path):
                file_path = os.path.join(root_dir, subfiles[0])
                tree = ET.parse(file_path)
                variable_root = tree.getroot()
                variable_schema_name[variable_root.get("schemaname")] = replace_words(
                    variable_root.get("schemaname"), words
                )
                variable_root.find("introducedversion").text = "1.0.0.0"
                tree.write(file_path)
                amend_file(file_path, words, components)

            os.rename(dir_path, new_dir_path)

    return variable_schema_name


def amend_workflows(path, words, components, connections, variables):
    workflows_path = f"{path}/Workflows"
    file_path = None
    new_file_path = None

    for root, dirs, files in os.walk(workflows_path):
        for file in files:
            file_path = os.path.join(root, file)
            amend_file(file_path, words, components, connections, variables)

            new_file_path = os.path.join(
                root, replace_words(replace_words(file, words), components)
            )
            os.rename(file_path, new_file_path)


def simplify_connections(
    api_name, logical_name, connection_dictionary, connection_api_counter
):
    if connection_dictionary.get(api_name) is None:
        connection_dictionary[api_name] = (
            logical_name,
            logical_name[0:-5] + str(uuid.uuid4())[-5:],
        )
        connection_api_counter[api_name] = 1

    elif logical_name not in list(
        map(
            lambda api_name: connection_dictionary[api_name][0],
            [api_name]
            + [
                api_name + "_" + str(n)
                for n in range(1, connection_api_counter[api_name] + 1)
            ],
        )
    ):
        connection_dictionary[api_name + "_" + connection_api_counter[api_name]] = (
            logical_name,
            logical_name[0:-5] + str(uuid.uuid4())[-5:],
        )

        connection_api_counter[api_name] += 1

    else:
        pass


def get_logical_name(connection):
    return connection[0]


def recreate_archive(path, new_solution_name, root):
    shutil.make_archive(f"{path}/{new_solution_name}", "zip", root)
    shutil.rmtree(root)


if __name__ == "__main__":
    zip_path, words_to_replace = parse_command_line()

    cwd = extract_zip_file(zip_path)
    components_guid = read_and_amend_solution_file(cwd, words_to_replace)

    connections = read_and_amend_customizations_file(
        cwd, words_to_replace, components_guid
    )

    variables_schema_names = read_and_amend_environmental_variables(
        f"{cwd}/environmentvariabledefinitions", words_to_replace, components_guid
    )

    amend_workflows(
        cwd, words_to_replace, components_guid, connections, variables_schema_names
    )

    new_solution_name = (
        replace_words(os.path.basename(zip_path).split("_")[0], words_to_replace)
        + "_1_0_0_0"
    )

    recreate_archive(os.path.dirname(zip_path), new_solution_name, cwd)
