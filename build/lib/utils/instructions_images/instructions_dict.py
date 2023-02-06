from utils.instructions_images import add_instructions

instructions_dict = {
    "create": {
        "images": [
            "utils/instructions_images/how_to_create/create_1.png",
            "utils/instructions_images/how_to_create/create_2.png"
        ],
        "instructions": add_instructions.create_instructions
    },
    "delete": {
        "images": [
            "utils/instructions_images/how_to_delete/delete_1.png",
            "utils/instructions_images/how_to_delete/delete_2.png"
        ],
        "instructions": add_instructions.delete_instructions
    },
    "read": {
        "images": [
            "utils/instructions_images/how_to_read/read_1.png",
            "utils/instructions_images/how_to_read/read_2.png",
            "utils/instructions_images/how_to_read/read_3.png"
        ],
        "instructions": add_instructions.read_instructions
    },
    "update": {
        "images": [
            "utils/instructions_images/how_to_update/update_1.png",
            "utils/instructions_images/how_to_update/update_2.png"
        ],
        "instructions": add_instructions.update_instructions
    },
    "upload": {
        "images": [
            "utils/instructions_images/how_to_upload/upload_1.png",
            "utils/instructions_images/how_to_upload/upload_2.png"
        ],
        "instructions": add_instructions.upload_instructions
    },
    "run": {
        "images": [
            "utils/instructions_images/how_to_run/run_1.png",
            "utils/instructions_images/how_to_run/run_2.png"
        ],
        "instructions": add_instructions.run_instructions
    },
}