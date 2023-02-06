from utils.pathway_generator import PathwayGenerator
import os
import yaml

if __name__ == "__main__":
    path = "Pathways"
    pathways_names = os.listdir(path)
    pathway_files = [os.path.join(path, pathway) for pathway in pathways_names
                     if os.path.isdir(os.path.join(path, pathway))]
    for pathway_file in pathway_files:
        print(f"Regenerating pathway {pathway_file}...")
        name = pathway_file.split("/")[-1]
        with open(os.path.join(pathway_file, "pathway.yaml"), "r") as f:
            pathway = yaml.safe_load(f)
        target_lessons = pathway["target_lessons"]
        if target_lessons:
            target_lessons = [target_lesson["name"] for target_lesson in target_lessons if "name" in target_lesson]
        source_lessons = pathway["source_lessons"]
        if source_lessons:
            source_lessons = [source_lesson["name"] for source_lesson in source_lessons if "name" in source_lesson]

        pathways = PathwayGenerator(
            name=name,
            target_lesson=target_lessons,
            source_lesson=source_lessons,
        )
        pathway_list = pathways.get_pathway()
        pathways.generate_files(
            pathway_list,
        )

    print("All pathways have been regenerated. Have a nice day! :)")
