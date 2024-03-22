from rdkit import Chem
from rdkit.Chem import Draw

class ChemistryExpert:
    def __init__(self):
        pass

    def parse_smile(self, smile_notation):
        mol = Chem.MolFromSmiles(smile_notation)
        return mol

    def get_molecule_properties(self, molecule):
        properties = {}
        properties['num_atoms'] = molecule.GetNumAtoms()
        properties['num_bonds'] = molecule.GetNumBonds()
        properties['formula'] = Chem.rdMolDescriptors.CalcMolFormula(molecule)
        properties['molecular_weight'] = Chem.rdMolDescriptors.CalcExactMolWt(molecule)
        return properties

    def visualize_molecule(self, molecule, filename=None):
        if filename:
            Draw.MolToFile(molecule, filename)
        else:
            Draw.MolToImage(molecule).show()
