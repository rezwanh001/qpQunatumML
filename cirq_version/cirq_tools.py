import cmath
import matplotlib.pyplot as plt
import numpy as np
import shutil
import subprocess
from cirq.contrib.qcircuit.qcircuit_diagram import circuit_to_latex_using_qcircuit
from pylatex import Document, NoEscape, Package
from qutip import Bloch
from tempfile import mkdtemp
import os 
import fitz

# def plot_circuit(circuit):
#     tex = circuit_to_latex_using_qcircuit(circuit)
#     doc = Document(documentclass='standalone',
#                    document_options=NoEscape('border=25pt,convert={density=300,outext=.png}'))
#     doc.packages.append(Package('amsmath'))
#     doc.packages.append(Package('qcircuit'))
#     doc.append(NoEscape(tex))
#     tmp_folder = mkdtemp()
#     doc.generate_tex(tmp_folder + '/circuit')
#     convert_log = open(tmp_folder+'/pdflatex.log', 'w')
#     proc = subprocess.Popen(['pdflatex', '-shell-escape', tmp_folder + '/circuit.tex'], cwd=tmp_folder, 
#            stdout = convert_log, stderr = convert_log)
#     proc.communicate()
#     convert_log.close()    
#     image = plt.imread(tmp_folder + '/circuit.png')
#     shutil.rmtree(tmp_folder)
#     plt.axis('off')
#     return plt.imshow(image)

def plot_circuit(circuit):
    tex = circuit_to_latex_using_qcircuit(circuit)
    doc = Document(documentclass='standalone',
                   document_options=NoEscape('border=25pt,convert={density=300,outext=.png}'))
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('qcircuit'))
    doc.append(NoEscape(tex))
    # tmp_folder = mkdtemp()
    tmp_folder = os.path.join(os.getcwd(), 'outputs')
    path_isExist = os.path.exists(tmp_folder)
    if not path_isExist: 
        os.mkdir(tmp_folder)

    doc.generate_tex(tmp_folder + '/circuit')
    convert_log = open(tmp_folder+'/pdflatex.log', 'w')
    proc = subprocess.Popen(['pdflatex', '-shell-escape', tmp_folder + '/circuit.tex'], cwd=tmp_folder, 
           stdout = convert_log, stderr = convert_log)
    proc.communicate()
    convert_log.close()

    pdffile = tmp_folder + '/circuit.pdf'
    path_pdffile_exist = os.path.exists(pdffile)
    # print(path_pdffile_exist)
    if path_pdffile_exist:
        doc = fitz.open(pdffile)
        page = doc.loadPage(0)  # number of page
        pix = page.get_pixmap()
        output = tmp_folder+"/circuit.png"
        pix.save(output)

    image = plt.imread(tmp_folder + '/circuit.png')
    # shutil.rmtree(tmp_folder)
    plt.axis('off')
    return plt.imshow(image)


def get_vector(alpha, beta):
    """
    Function to compute 3D Cartesian coordinates
    from 2D qubit vector.
    """

    # get phases
    angle_alpha = cmath.phase(alpha)
    angle_beta = cmath.phase(beta)

    # avoiding wrong normalization due to rounding errors
    if cmath.isclose(angle_alpha, cmath.pi):
        angle_alpha = 0
    if cmath.isclose(angle_beta, cmath.pi):
        angle_beta = 0

    if (angle_beta < 0 and angle_alpha < angle_beta) or (angle_beta > 0 and angle_alpha > angle_beta):
            denominator = cmath.exp(1j*angle_beta)
    else:
            denominator = cmath.exp(1j*angle_alpha)

    # eliminate global phase
    alpha_new = alpha/denominator
    beta_new = beta/denominator

    # special case to avoid division by zero
    if abs(alpha) == 0 or abs(beta) == 0:
        if alpha == 0:
            return [0,0,-1]
        else:
            return [0,0,1]
    else:
        # compute theta and phi from alpha and beta
        theta = 2*cmath.acos(alpha_new)
        phi = -1j*cmath.log(beta_new/cmath.sin(theta/2))

        # compute the Cartesian coordinates
        x = cmath.sin(theta)*cmath.cos(phi)
        y = cmath.sin(theta)*cmath.sin(phi)
        z = cmath.cos(theta)

    return [x.real, y.real, z.real]


def plot_quantum_state(amplitudes):
    """
    Thin function to abstract the plotting on the Bloch sphere.
    """
    bloch_sphere = Bloch()
    vec = get_vector(amplitudes[0], amplitudes[1])
    bloch_sphere.add_vectors(vec)
    bloch_sphere.show()
    bloch_sphere.clear()


def plot_histogram(counts):
    x = np.arange(len(counts))
    plt.bar(x, counts.values())
    plt.xticks(x, counts.keys())
    plt.show()
