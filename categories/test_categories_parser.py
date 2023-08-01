import yaml
import json

# Load the YAML OpenAPI specification
with open("categories.yaml", "r") as spec_file:
    yaml_data = yaml.safe_load(spec_file)


def create_python_object(schema, class_name, attr_values=None):
    cls_dict = {}

    if "properties" in schema:
        for prop, prop_data in schema["properties"].items():
            if "default" in prop_data:
                # Use the specified default value if available
                cls_dict[prop] = prop_data["default"]
            elif "type" in prop_data:
                # Set default values for different data types
                data_type = prop_data["type"]
                if data_type == "string":
                    cls_dict[prop] = ""
                elif data_type == "integer":
                    cls_dict[prop] = 0
                elif data_type == "boolean":
                    cls_dict[prop] = False
            elif "$ref" in prop_data:
                ref_class_name = prop_data["$ref"].split("/")[-1]
                cls_dict[prop] = create_python_object(
                    schema["components"]["schemas"][ref_class_name], ref_class_name
                )

    def init_method(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    cls = type(class_name, (), {"__init__": init_method})

    return cls(**(attr_values or cls_dict))


response_schema = yaml_data["paths"]["/users"]["get"]["responses"]["200"]["content"][
    "application/json"
]["schema"]

json_data = json.loads(open("categories.json", "r").read())
categories = create_python_object(response_schema["items"], "categories", json_data)

for attr, value in vars(categories).items():
    print(f"{attr}: {value}\n")
