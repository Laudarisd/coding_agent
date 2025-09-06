from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_contents import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
import os
import glob

WORKING_DIRECTORY = "calculator"

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

def resolve_file_path(filename, working_directory=WORKING_DIRECTORY):
    """
    If filename is just a file (no /), search all subdirs in working_directory for it and return the first match.
    Otherwise, return as is.
    """
    if not isinstance(filename, str):
        return filename
    if "/" not in filename:
        matches = glob.glob(os.path.join(working_directory, "**", filename), recursive=True)
        if matches:
            # Return relative path from working_directory
            return os.path.relpath(matches[0], working_directory)
    return filename

def normalize_path_arg(arg, working_directory=WORKING_DIRECTORY):
    """
    Normalize a path argument by removing redundant working directory prefixes and mapping root requests.
    """
    if not isinstance(arg, str):
        return arg
    # Remove leading working_directory/ if present
    if arg == working_directory:
        return "."
    if arg.startswith(working_directory + "/"):
        return arg[len(working_directory) + 1:]
    return arg

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = dict(function_call_part.args)
    args["working_directory"] = WORKING_DIRECTORY
    # Normalize directory and file_path arguments
    if "directory" in args:
        args["directory"] = normalize_path_arg(args["directory"])
    if "file_path" in args:
        # Always resolve file_path for relevant functions
        args["file_path"] = resolve_file_path(normalize_path_arg(args["file_path"]))
    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")
    func = function_map.get(function_name)
    if not func:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    try:
        result = func(**args)
    except Exception as e:
        result = f"Error: {type(e).__name__}: {e}"
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )
