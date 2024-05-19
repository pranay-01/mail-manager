ACCESS_SCOPES = ["https://mail.google.com/"]

RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "predicate": {"type": "string"},
        "conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field_name": {"type": "string"},
                    "predicate": {"type": "string"},
                    "value": {"type": ["string", "integer"]}
                },
                "required": ["field_name", "predicate", "value"],
                "additionalProperties": False
            },
        },
        "actions": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["predicate", "conditions", "actions"],
    "additionalProperties": False
}
