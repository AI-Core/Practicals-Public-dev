from utils.pathway_generator import PathwayGenerator
import yaml
import os
import glob

pathway_dirs = glob.glob('Pathways/*')
pathway_dirs = [pathway_dir for pathway_dir in pathway_dirs if os.path.isdir(pathway_dir)]

for pathway_dir in pathway_dirs:
    print("Regenerating pathway: ", pathway_dir)
    pathway_specs = pathway_dir + '/pathway.yaml'
    with open(pathway_specs, 'r') as f:
        pathway = yaml.safe_load(f)

    source_lesson: list = pathway['source_lessons']
    source_lesson_names = None
    if source_lesson:
        source_lesson_names = [lesson['name'] for lesson in source_lesson]
    
    target_lesson: list = pathway['target_lessons']
    target_lesson_names = None
    if target_lesson:
        target_lesson_names = [lesson['name'] for lesson in target_lesson]
    description: str = pathway['description']
    name = pathway_dir.split('/')[-1]
    pathway_generator = PathwayGenerator(
        name=name,
        source_lesson=source_lesson_names,
        target_lesson=target_lesson_names,
        description=description,
        delete_intermediate_lessons=True
    )
    pathway_generator.debug_pathway()
    pathway_list = pathway_generator.get_pathway()
    pathway_generator.generate_files(pathway_list)


