from workflow_graph.__main__ import ContentGraph
from utils.client import Lesson
import networkx as nx
from typing import List, Union, Tuple, Optional
from dataclasses import dataclass
import os
import yaml
import uuid


@dataclass
class PathwayGraphGenerator(ContentGraph):
    '''
    Generate a pathway from a source lesson to a target lesson

    The pathway contains all the lessons that are required to
    reach the target lesson. In some cases, there might be more
    sources to the target lesson, and in that case, we include
    all the paths to the target lesson.

    Parameters
    ----------
    name: str
        The name of the pathway
    target_lesson : Union[str, List[str]]
        The target lesson(s)
    source_lesson : Union[str, List[str], None]
        The source lesson. If None, it will be the first lesson
        in the pathway. If a list, each lesson indicates a different
        source lesson to the target lesson
    stop_prerequisites_from : Union[str, List[str], None]
        The lesson(s) from where the prerequisites should stop
        If they are part of the main pathway, the prerequisites that will be
        ignored will be the ones that are not in the pathway
    delete_intermediate_lessons : bool
        If a list of source lessons is provided, and one of the lessons
        is a predecessor of another, the lessons between the two will
        be deleted.
        Otherwise, if one of the lessons is a predecessor of another,
        the class will raise an error
    description : str
        The description of the pathway. If None, it will be generated
        automatically in the post_init method
    list_lessons_for_debugging : List[str]
        List of lessons to use for debugging. If None, it will use
        all the lessons in the content
        This is used for debugging purposes to check what prerequisites
        shouldn't be included in the meta files

    Attributes
    ----------
    graph : nx.DiGraph
        The graph of All the lessons in the content
    pathway_subgraph : nx.DiGraph
        The graph of the lessons only in the pathway
    '''
    name: str
    source_lesson: Union[str, List[str], None] = None
    target_lesson: Union[str, List[str], None] = None
    stop_prerequisites_from: Union[str, List[str], None] = None
    delete_intermediate_lessons: bool = True
    list_lessons_for_debugging: List[str] = None
    verbose: bool = False

    def __post_init__(
        self
    ) -> None:
        super().__init__()
        assert self.target_lesson or self.source_lesson, \
            "You must provide at least one of the source or target lessons"
        # Converts lessons from strings to lists to keep consistency
        if isinstance(self.target_lesson, str):
            self.target_lesson = [self.target_lesson]
        if isinstance(self.source_lesson, str):
            self.source_lesson = [self.source_lesson]

        if self.list_lessons_for_debugging:
            self.graph = self.get_graph_from_lesson_subset(self.list_lessons_for_debugging)
            # When debugging, we don't want to remove the source lesson
            # predecessors because we want to see all predecessors that
            # should be removed
        else:
            self.graph = self.get_graph_from_lesson_subset(self.content.lessons)
            if self.source_lesson:
                self._remove_multiple_source_predecessors()

        nodes_to_targets = self._get_nodes_to_target_and_set_target_lessons(
            source_lesson=self.source_lesson,
            target_lesson=self.target_lesson
        )
        if self.stop_prerequisites_from:
            if isinstance(self.stop_prerequisites_from, str):
                self.stop_prerequisites_from = [self.stop_prerequisites_from]
            self._remove_prerequisites_from(self.stop_prerequisites_from)

        self.pathway_subgraph = self._get_pathway_subgraph(nodes_to_targets)
        all_simple_paths_same_node = self._get_all_simple_paths(
            target_lessons=self.target_lesson,
            graph=self.pathway_subgraph
        )
        self._remove_redundant_paths(all_simple_paths_same_node)
        self._remove_unnecessary_edges()

    def plot_graph_pathway(
        self,
        save_dir: str = None
    ) -> None:
        '''
        Plots the pathway graph and saves it to a file
        if save is True

        Parameters
        ----------
        save : bool
            Whether to save the graph to a file
        '''
        graph_img = super().plot_graph(self.pathway_subgraph)
        if save_dir:
            filepath = f"{save_dir}/graph.png"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            graph_img.save(filepath)

    def generate_files(
        self,
        save_path: str = None,
        create_yaml: bool = True,
        create_graph: bool = True
    ) -> None:
        '''
        Generates the files for the pathway

        Parameters
        ----------
        save_path : str
            The path to save the files to
        create_yaml : bool
            Whether to create the yaml file
        create_graph : bool
            Whether to create the graph
        '''
        if create_yaml:
            self._generate_yaml(save=True)
        if create_graph:
            self.plot_graph(graph=self.pathway_subgraph,
                            show=False,
                            save_path=save_path + "/graph.png")

    def _remove_prerequisites_from(
        self,
        offending_lesson: List[str]
    ) -> None:
        '''
        Removes the prerequisites from the lessons provided

        Parameters
        ----------
        lessons : List[str]
            The lessons from where the prerequisites should be removed
        '''

        for source in self.source_lesson:
            for target in self.target_lesson:
                simple_paths = nx.all_simple_paths(
                    self.graph,
                    source=source,
                    target=target
                )
        
        unique_lessons = set()
        for path in simple_paths:
            unique_lessons.update(path)

        lesson_ids = []
        for lesson in unique_lessons:
            # Get the ids of all lessons
            lesson_ids.append(self.content.get_id_from_lesson_name(lesson))

        prereqs_to_remove = []
        for lesson in offending_lesson:
            # Get the lesson object
            lesson_obj = [le for le in self.content.lessons if le.name == lesson][0]
            # Get the ids of the prerequisites
            prereq_ids = lesson_obj.prerequisites
            # Get the ids of the lessons that are not in the pathway
            prereqs_to_remove.extend([prereq for prereq in prereq_ids if prereq not in lesson_ids])

        for lesson in prereqs_to_remove:
            to_remove = self.content.get_lesson_from_id(lesson)
            self._remove_predecessors(
                lesson=to_remove.name,
                include_node=True
            )

    def _get_nodes_to_target_and_set_target_lessons(
        self,
        source_lesson: Union[str, List[str], None],
        target_lesson: Union[str, List[str], None],
    ) -> List[str]:
        '''
        Gets all the nodes to reach the target lesson

        In case the user doesn't provide a target lesson,
        this function will find the target lessons based on
        all the possible paths from the source lessons to the
        leaf nodes
        '''
        if target_lesson is None:
            end_nodes = [n for n, d in self.graph.out_degree() if d == 0]
            # Get all the upstream nodes for each end node and remove those that don't include the source lesson
            nodes_to_target = []
            self.target_lesson = []
            for source in self.source_lesson:
                simple_paths = nx.all_simple_paths(
                    self.graph,
                    source=source,
                    target=end_nodes
                )
                for path in simple_paths:
                    nodes_to_target.extend(path)
                    self.target_lesson.append(path[-1])
            nodes_to_target = list(set(nodes_to_target))
        else:
            if isinstance(target_lesson, str):
                target_lesson = [target_lesson]

            nodes_to_target = []
            for lesson in target_lesson:
                upstream = self._get_upstream_nodes(
                    lesson,
                    include_node=True
                )
                nodes_to_target.extend(upstream)
            nodes_to_target = list(set(nodes_to_target))

            if self.source_lesson:
                for source_lesson in self.source_lesson:
                    assert source_lesson in nodes_to_target, \
                        f"There is no path from '{source_lesson}' " + \
                        "to any of the following lessons\n" + \
                        f"'{' '.join(target_lesson)}'.\n" + \
                        "Please check the spelling of the lessons " + \
                        "and make sure that they are in the graph"
        return nodes_to_target

    def _generate_yaml(
        self,
        save: bool = False,
    ) -> None:
        '''
        Generates the yaml file for the pathway

        Parameters
        ----------
        save : bool
            Whether to save the yaml file
        description : str
            The description of the pathway. It defaults to None,
            in which case the description is the same as the name
        '''
        upstream_nodes = self._get_upstream_nodes(
            self.target_lesson,
            include_node=True,
            graph=self.pathway_subgraph
        )
        upstream_nodes = upstream_nodes[::-1]
        yaml_list_dict = []
        for node in upstream_nodes:
            incoming_edges = self.pathway_subgraph.in_edges(node)
            yaml_dict = {}
            lesson_id = self.pathway_subgraph.nodes[node]['id']
            yaml_dict['lesson'] = node
            yaml_dict['id'] = lesson_id
            yaml_dict['depends_on'] = []
            for incoming_edge in incoming_edges:
                lesson_id = self.pathway_subgraph.nodes[incoming_edge[0]]['id']
                yaml_dict['depends_on'].append(lesson_id)
            yaml_list_dict.append(yaml_dict)

        for lesson in yaml_list_dict:
            lesson_id = lesson['id']
            lesson['level'] = self._get_lesson_level(yaml_list_dict,
                                                     lesson_id)

        if save:
            folderpath = f"Pathways/{self.name}"
            filepath = f"{folderpath}/pathway.yaml"
            if not os.path.exists(folderpath):
                os.makedirs(folderpath)

            # If the file exists, don't change the id
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    old_specs = yaml.safe_load(f)
                yaml_id = old_specs['id']
            else:
                yaml_id = None

            with open(filepath, "w") as f:
                f.write(f"name: {self.name}\n")
                if yaml_id:
                    f.write(f'id: {yaml_id}\n')
                else:
                    f.write(f'id: {uuid.uuid4()}\n')
                f.write("pathway: \n")
                for yaml_dict in yaml_list_dict:
                    f.write(yaml.dump([yaml_dict],
                                      default_flow_style=False,
                                      sort_keys=False,
                                      indent=2))
                    f.write("\n")

    def _get_lesson_level(
        self,
        lessons: List[dict],
        lesson_id: str
    ) -> int:
        '''
        Add an index to each lesson in the list of lessons
        based on the level of dependency

        Parameters
        ----------
        lessons : List[dict]
            The list of lessons
        lesson : str
            The lesson to get the index of
        '''
        lesson_to_add = [lesson for lesson in lessons
                         if lesson['id'] == lesson_id][0]
        if len(lesson_to_add['depends_on']) == 0:
            return 0
        elif 'level' in lesson_to_add:
            return lesson_to_add['level']
        else:
            deps_level = []
            for dependency in lesson_to_add['depends_on']:
                deps_level.append(self._get_lesson_level(lessons,
                                                         dependency))
            lesson_to_add['level'] = max(deps_level) + 1
            return lesson_to_add['level']

    def _get_pathway_subgraph(
        self,
        nodes: List[str]
    ) -> nx.DiGraph:
        '''
        Get the subgraph from source to target

        Parameters
        ----------
        target_node : Union[List[str], str]
            The target node(s)

        Returns
        -------
        nx.DiGraph
            The subgraph that contains all the nodes from the source
            to the target
        '''
        subgraph = self.graph.subgraph(nodes)
        subgraph = nx.DiGraph(subgraph)
        return subgraph

    def _remove_predecessors(
        self,
        lesson: str,
        include_node: bool = False
    ) -> None:
        '''
        Remove all predecessors of the source lesson
        '''
        upstream = self._get_upstream_nodes(
            lesson,
            include_node=include_node
        )
        removing_nodes = [lesson] + upstream
        if self.verbose:
            print(f"Removing the following nodes: {removing_nodes}")
        self.graph.remove_nodes_from(upstream)

    def _remove_multiple_source_predecessors(
        self,
        lessons: List[str] = None
    ) -> None:
        '''
        Remove all predecessors of the source lessons

        Parameters
        ----------
        lessons : List[str], optional
            The lessons to remove the predecessors
            if None, use self.source_lesson, by default None

        Raises
        ------
        AssertionError
            If there is a source lesson that is already a predecessor
            of another source lesson and the attribute delete_intermediate
            is False
        '''
        if not lessons:
            lessons = self.source_lesson

        # Get all the upstream nodes for each source lesson
        all_upstream = {}
        for source_lesson in lessons:
            upstream = self._get_upstream_nodes(source_lesson)
            all_upstream[source_lesson] = upstream

        # Check that there is no source lesson that is a predecessor
        # If self.delete_intermediate_lessons is False, then we raise
        # an error. If it is True, then we remove the lessons between
        # the source lessons
        nodes_removed = []
        for source_lesson in lessons:
            for other_source_lesson in lessons:
                if source_lesson != other_source_lesson and \
                        not self.delete_intermediate_lessons:
                    assert source_lesson not in all_upstream[other_source_lesson], \
                        f"Source lesson '{source_lesson}' is a " + \
                        f"predecessor of '{other_source_lesson}'. " + \
                        "Please check that the source lessons are correct."
                elif source_lesson != other_source_lesson and \
                        self.delete_intermediate_lessons:
                    if source_lesson in all_upstream[other_source_lesson]:
                        nodes_between = self._get_nodes_between(
                            source_lesson,
                            other_source_lesson
                        )

                        if self.verbose:
                            print(f"Removing nodes '{nodes_between}'")

                        for node in nodes_between:
                            if node not in nodes_removed:
                                self.graph.remove_node(node)
                                nodes_removed.append(node)

        unique_upstream = set()
        for upstream in all_upstream.values():
            # Delete all the nodes that are not in
            # the source lesson list
            unique_upstream = unique_upstream.union(upstream)
        unique_upstream = unique_upstream.difference(lessons)
        for node in unique_upstream:
            if node not in nodes_removed:
                self.graph.remove_node(node)
                nodes_removed.append(node)
                if self.verbose:
                    print(f"Removing node '{node}'")

    def _get_nodes_between(
        self,
        source: str,
        target: str
    ) -> List[str]:
        '''
        Get the nodes between source and target

        Parameters
        ----------
        source : str
            The source node
        target : str
            The target node

        Returns
        -------
        List[str]
            The list of nodes between source and target
        '''
        nodes_between = self._get_nodes_to_target_and_set_target_lessons(
            source_lesson=source,
            target_lesson=target
        )
        subgraph = self._get_pathway_subgraph(nodes_between)
        nodes_between = nx.shortest_path(subgraph, source, target)
        # Remove source and target
        nodes_between = nodes_between[1:-1]
        return nodes_between

    def _remove_redundant_paths(
        self,
        simple_paths_same_node: List[List[str]]
    ) -> None:
        '''
        Remove redundant paths

        For example, if there are two paths from A to B, and one of
        them is a subset of the other, then we remove the subset
        We take the longest path, so that we don't skip any lessons

        Parameters
        ----------
        simple_paths_same_node : List[List[str]]
        '''
        removed_edges = []
        for simple_path_same_node in simple_paths_same_node:
            simple_path_same_node = sorted(simple_path_same_node,
                                           key=lambda x: len(x),
                                           reverse=True)
            offending_paths = []
            not_offending_paths = []
            for simple_path in simple_path_same_node:
                unique_nodes = set(simple_path)
                for not_offending_path in not_offending_paths:
                    if unique_nodes.issubset(set(not_offending_path)):
                        offending_paths.append(
                            (simple_path,
                             not_offending_path)
                        )
                        break
                else:
                    not_offending_paths.append(simple_path)

            for offending_nodes, not_offending_nodes in offending_paths:
                offending_edges = []
                desired_edges = []
                for node_n in range(len(offending_nodes) - 1):
                    offending_edges.append((offending_nodes[node_n],
                                            offending_nodes[node_n + 1]))
                for node_n in range(len(not_offending_nodes) - 1):
                    desired_edges.append((not_offending_nodes[node_n],
                                          not_offending_nodes[node_n + 1]))

                difference = list(set(offending_edges) - set(desired_edges))
                for edge in difference:
                    if edge in removed_edges:
                        continue
                    if self.verbose:
                        print(f"Removing edge '{edge[0]} -> {edge[1]}'")
                    self.pathway_subgraph.remove_edge(*edge)
                    removed_edges.append(edge)
                    if self.list_lessons_for_debugging and self.verbose:
                        message = f"The dependency from '{edge[0]}' to '{edge[1]}' " + \
                                  "is redundant and should be removed in the meta files"
                        print(message)

    def _remove_unnecessary_edges(
        self
    ) -> None:
        '''
        Remove connections that are not involved in the pathway
        '''
        for node in self.pathway_subgraph.nodes:
            in_edges = self.pathway_subgraph.in_edges(node)
            out_edges = self.pathway_subgraph.out_edges(node)
            for in_edge in in_edges:
                if in_edge[0] not in self.pathway_subgraph.nodes:
                    self.pathway_subgraph.remove_edge(*in_edge)
            for out_edge in out_edges:
                if out_edge[1] not in self.pathway_subgraph.nodes:
                    self.pathway_subgraph.remove_edge(*out_edge)

    def _get_all_simple_paths(
        self,
        target_lessons: Optional[List[str]],
        graph: nx.DiGraph = None
    ) -> List[List[str]]:
        '''
        Get all simple paths from all roots to a target node
        Or, another way to say it, get all simple paths to get to a target node

        Parameters
        ----------
        target_lessons : List[str], optional
            List of target lessons to get simple paths to.
        graph : nx.DiGraph
            Main graph to get upstream nodes from. By default, the main graph

        Returns
        -------
        simple_paths_same_node : List[List[str]]
            List of simple paths to get to the target node
            Each nested list can have multiple simple paths and all of them
            start from the same root node
        '''
        if graph is None:
            graph = self.graph
        if target_lessons is None:
            target_lessons = [n for n, d in graph.out_degree() if d == 0]
        upstream = []
        for lesson in target_lessons:
            upstream_target = self._get_upstream_nodes(
                lesson,
                include_node=True
            )
            upstream.extend(upstream_target)

        upstream_graph = graph.subgraph(upstream)
        # We obtained a subgraph of the main graph,
        # now we need to see which nodes
        # are roots in this subgraph
        roots = [n for n, d in upstream_graph.in_degree() if d == 0]

        simple_paths_same_node = []
        for root in roots:
            simple_paths = nx.all_simple_paths(
                graph,
                root,
                self.target_lesson,
            )
            simple_paths_same_node.append(list(simple_paths))

        return simple_paths_same_node

    def _get_upstream_nodes(
        self,
        node: str,
        include_node: bool = False,
        graph: nx.DiGraph = None
    ) -> List[str]:
        '''
        Get all upstream nodes of a node in a graph
        It returns a list of nodes by default,

        Parameters
        ----------
        node : str
            Node to get upstream nodes from. It is the name of the lesson
        include_node : bool, optional
            If True, the node is included in the list, by default False
        graph : nx.DiGraph, optional
            Graph to get upstream nodes from, if None, the main graph is used
        '''
        if graph is None:
            graph = self.graph
        upstream = nx.traversal.bfs_tree(graph, node, reverse=True)
        if include_node:
            upstream = [n for n in upstream]
        else:
            upstream = [n for n in upstream if n != node]
        return upstream

    def _generate_description(
        self
    ) -> str:
        '''
        Generate a description of the pathway

        Returns
        -------
        description : str
            Description of the pathway
        '''
        if self.target_lesson:
            description = 'Pathway to get to the lesson(s) '
            target_names = [lesson.name for lesson in self.target_lesson]
            description += ', '.join(target_names)
        else:
            description = 'Pathway to get to all lessons '
        if self.source_lesson:
            source_names = [lesson.name for lesson in self.source_lesson]
            description += ' from the lesson(s) ' + ', '.join(source_names)
        return description


@dataclass
class PathwayGenerator(PathwayGraphGenerator):
    '''
    Class to generate pathways for a target lesson
    '''

    def __post_init__(
        self
    ) -> None:
        super().__post_init__()
        self.lessons = self.content.lessons

        if self.target_lesson:
            self.target_lesson = [self._get_lesson_by_name(lesson)
                                  for lesson in self.target_lesson]

        if self.source_lesson:
            self.source_lesson = [self._get_lesson_by_name(lesson)
                                  for lesson in self.source_lesson]

        if self.stop_prerequisites_from:
            self.stop_prerequisites_from = [
                self._get_lesson_by_name(lesson)
                for lesson in self.stop_prerequisites_from
            ]

        # This part here is redundant, but for now we need it because of the
        # current state of the dependencies bypassing certain lessons
        self.lessons_to_keep = [n for n in self.pathway_subgraph.nodes]

    def get_pathway(
        self
    ) -> List[str]:
        '''
        Get the needed prerequisites
        '''
        prereqs = self.get_all_prerequisites()
        lessons_in_pathway = [
            {"name": lesson.name, "id": str(lesson.id)}
            for lesson in prereqs
            if lesson.name in self.lessons_to_keep
        ]

        return lessons_in_pathway

    def debug_pathway(
        self
    ) -> None:
        '''
        Prints the pathway redundancies so they are removed from 
        the meta data
        '''
        prereqs = self.get_all_prerequisites()
        if self.target_lesson:
            target_lesson = [lesson.name for lesson in self.target_lesson]
        else:
            target_lesson = None
        if self.source_lesson:
            source_lesson = [lesson.name for lesson in self.source_lesson]
        else:
            source_lesson = None
        PathwayGraphGenerator(
            self.name,
            target_lesson=target_lesson,
            source_lesson=source_lesson,
            delete_intermediate_lessons=True,
            list_lessons_for_debugging=prereqs,
            verbose=True
        )

    def generate_files(
        self,
        pathway: List[Tuple[str, str]],
        description: str = None,
        membership_key: List[str] = None,
        create_graph: bool = True,
        create_yaml: bool = True,
        root_dir: str = 'Pathways'
    ) -> None:
        '''
        Generate the files for the pathway

        Parameters
        ----------
        pathway : List[Tuple[str, str]]
            List of tuples with the name of the lesson and the id
        create_graph : bool, optional
            If True, a graph is created, by default True
        create_yaml : bool, optional
            If True, a yaml file is created, by default True
        '''
        save_dir = os.path.join(root_dir, self.name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        if create_graph:
            self.plot_graph(
                graph=self.pathway_subgraph,
                show=False,
                save_path=(save_dir + '/graph.png'))
        if create_yaml:
            self._generate_yaml(
                pathway,
                save_dir,
                description=description,
                membership_key=membership_key
            )

    def _generate_yaml(
        self,
        pathway: List[Tuple[str, str]],
        save_dir: str,
        description: str = None,
        membership_key: List[str] = None
    ) -> None:
        '''
        Generate a yaml file with the pathway.

        If a description is provided, it will overwrite the existing one.
        If the yaml file doesn't have a description, and no description is
        provided, the description will be a generated one.

        Parameters
        ----------
        pathway : List[Tuple[str, str]]
            List of tuples with the name of the lesson and the id
        save_dir : str
            Directory where the yaml file will be saved
        description : str, optional
            Description of the pathway, by default None
        membership_key : List[str], optional
            Membership keys for the pathway, by default None
        '''
        yaml_dir = os.path.join(save_dir, 'pathway' + '.yaml')

        if os.path.exists(yaml_dir):
            with open(yaml_dir, 'r') as f:
                pathway_dict = yaml.safe_load(f)
            if description:
                pathway_dict['description'] = description
            elif 'description' not in pathway_dict:
                pathway_dict['description'] = self._generate_description()

        else:
            pathway_dict = {
                'name': self.name,
                'id': str(uuid.uuid4()),
                'description': self._generate_description()
            }

        if membership_key:
            self.__upsert_membership_keys(
                membership_key,
                pathway_dict['id']
            )

        target_lessons = [
            {"name": lesson.name,
             "id": str(lesson.id)}
            for lesson in self.target_lesson
        ]
        pathway_dict['target_lessons'] = target_lessons
        if self.source_lesson:
            source_lesson = [
                {"name": lesson.name,
                 "id": str(lesson.id)}
                for lesson in self.source_lesson
            ]
        else:
            source_lesson = None
        pathway_dict['source_lessons'] = source_lesson

        if self.stop_prerequisites_from:
            stop_prerequisites_from = [
                {"name": lesson.name,
                 "id": str(lesson.id)}
                for lesson in self.stop_prerequisites_from
            ]
        else:
            stop_prerequisites_from = None
        pathway_dict['stop_prerequisites_from'] = stop_prerequisites_from

        pathway_dict['lessons'] = pathway

        print('Saving file in ' + yaml_dir + '...')
        with open(yaml_dir, 'w') as f:
            yaml.safe_dump(pathway_dict, f, sort_keys=False)

    def __upsert_membership_keys(
        self,
        membership_key: List[str],
        pathway_id: str,
        membership_key_path: str = 'Pathways/membership_keys.yaml'
    ) -> None:
        '''
        Add membership keys to the membership_keys.yaml file
        '''
        if isinstance(membership_key, str):
            membership_key = [membership_key]
        if os.path.exists(membership_key_path):
            with open(membership_key_path, 'r') as f:
                existing_membership_keys: List[dict] = yaml.safe_load(f)
            for name in membership_key:
                found = False
                for membership_key_dict in existing_membership_keys:
                    existing_pathways = membership_key_dict['pathways']
                    existing_pathways_ids = [pathway['id'] for pathway in existing_pathways]
                    if membership_key_dict['name'] == name and (pathway_id not in existing_pathways_ids):
                        membership_key_dict['pathways'].append({
                            'id': pathway_id,
                            'name': self.name,
                        })
                        found = True
                        break
                    elif membership_key_dict['name'] == name and (pathway_id in existing_pathways_ids):
                        found = True
                        break
                if not found:
                    existing_membership_keys.append({
                        'name': name,
                        'pathways': [{
                            'id': pathway_id,
                            'name': self.name,
                        }]
                    })

            with open(membership_key_path, 'w') as f:
                yaml.safe_dump(existing_membership_keys, f, sort_keys=False)
        else:
            membership_key_dict = []
            for name in membership_key:
                membership_key_dict.append({
                    'name': name,
                    'pathways': [{
                        'id': pathway_id,
                        'name': self.name,
                    }]
                })
            with open(membership_key_path, 'w') as f:
                yaml.safe_dump(membership_key_dict, f, sort_keys=False)

    def get_all_prerequisites(
        self
    ) -> List[str]:
        '''
        Get all prerequisites of a lesson
        '''
        prereqs = []
        if self.source_lesson and self.target_lesson:
            for lesson in self.target_lesson:
                prereqs_lesson = self.content.get_recursive_prerequisites(lesson=lesson,
                                                                          source_lesson=self.source_lesson)
                # appends the target lesson to the list of prerequisites
                prereqs_lesson.append(lesson)
                prereqs.append(prereqs_lesson)
        elif self.source_lesson:
            pass
        else:
            for lesson in self.target_lesson:
                prereqs_lesson = self.content.get_recursive_prerequisites(
                    lesson=lesson)
                prereqs_lesson.append(lesson)
                prereqs.append(prereqs_lesson)

        # The first element of the final list should be the a source lesson
        # with the longest number of prerequisites.

        sorted_prereqs = sorted(prereqs, key=len, reverse=True)
        prereqs = self.__remove_duplicates(sorted_prereqs)
        return prereqs

    @staticmethod
    def __remove_duplicates(
        prereqs_list: List[List[Lesson]]
    ) -> List[Lesson]:
        # Flatten the list
        prereqs_list = [item for sublist in prereqs_list for item in sublist]
        unique_list = []
        for elem in prereqs_list:
            if elem not in unique_list:
                unique_list.append(elem)

        return unique_list

    def _get_lesson_by_name(
        self,
        lesson_name: str
    ) -> Lesson:
        '''
        Get a lesson by name
        '''
        lessons = [
            lesson for lesson in self.lessons if lesson.name == lesson_name]
        if len(lessons) == 0:
            raise ValueError(f'Lesson {lesson_name} not found')
        elif len(lessons) > 1:
            raise ValueError(
                f'More than one lesson with the name {lesson_name} found')
        else:
            return lessons[0]


if __name__ == "__main__":
    # ["Lambda Functions", "Decorators", "Generators", "Magic Methods", "Class Decorators", "Typing", "Docstrings"],
    pathways = PathwayGenerator(
        name='Towards ChatGPT',
        source_lesson=['Essential ML Concepts'],
        target_lesson=['Word Analogies'],
        stop_prerequisites_from=['Understanding Neural Networks'],
        delete_intermediate_lessons=True,
        verbose=True
    )
    pathways.debug_pathway()
    pathway_list = pathways.get_pathway()
    pathways.generate_files(
        pathway_list,
        description='Learn the deep learning concepts that make ChatGPT possible',
        membership_key='oxford2023',
    )
