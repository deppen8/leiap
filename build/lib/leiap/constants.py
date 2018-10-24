"""
This module contains functions to access some commonly-used constants and their translations
"""


#######################################################################################################################


def get_waretypes(lang='both'):
    """Access the waretypes used in the database

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    requested_names : dict, list
        A dictionary or list of waretypes. If lang='both', return a dictionary of english:catalan names

    """
    waretypes = {
        'common ware': 'comuna',
        'unknown_waretype': 'desconeguda',
        'transport': 'transport',
        'storage': 'emmagatzematge',
        'fine ware': 'fina',
        'cooking ware': 'cuina',
        'table ware': 'taula',
        'other': 'altre',
        'ritual': 'ritual'
    }

    requested_names = None

    if lang == 'both':
        requested_names = waretypes
    elif lang == 'eng':
        requested_names = list(waretypes.keys())
    elif lang == 'cat':
        requested_names = list(waretypes.values())

    return requested_names


#######################################################################################################################


def get_vesselparts(lang='both'):
    """Access the vessel parts used in the database

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    requested_names : dict, list
        If language is 'both', then a dict is returned; otherwise a list
    """
    vessel_parts = {
        'base': 'base',
        'body': 'cos',
        'carination': 'carinada',
        'handle': 'nansa',
        'lid': 'tapa',
        'neck': 'coll',
        'other_vesselpart': 'altra part',
        'rim': 'vora',
        'shoulder': 'espatlla',
        'unknown_vesselpart': 'part desconeguda'
    }

    requested_names = None

    if lang == 'both':
        requested_names = vessel_parts
    elif lang == 'eng':
        requested_names = list(vessel_parts.keys())
    elif lang == 'cat':
        requested_names = list(vessel_parts.values())

    return requested_names


#######################################################################################################################


def get_talaiotic(lang='both'):
    """Access Talaiotic period productions

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Talaiotic period productions. If lang='both', return dict, else return a list
    """
    p = {'Punic amphora': 'Àmfora púnica',
         'Talaiotic pottery': 'Ceràmica Talaiòtica',
         'Attic black glaze pottery': 'Ceràmica de Vernís Negre Àtica',
         'Central Mediterranean punic amphora': 'Àmfora púnica del Mediterrani Central'
         }

    productions = None

    if lang == 'both':
        productions = p
    elif lang == 'eng':
        productions = list(p.keys())
    elif lang == 'cat':
        productions = list(p.values())

    return productions


#######################################################################################################################


def get_balearic(lang='both'):
    """Access Balearic period productions

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Balearic period productions. If lang='both', return dict, else return a list
    """
    p = {'Punic Ebusitan amphora': 'Àmfora Punicoebusitana',
         'South Italian amphora - Volcanic': 'Àmfora Sud-itàlica - Pasta Volcànica',
         'Greco-Italic amphora': 'Àmfora greco-itàlica',
         'Iberian amphora': 'Àmfora ibèrica',
         'Italic amphora': 'Àmfora Itàlica',
         'Campanian black glazed pottery A': 'Ceràmica de Vernís Negre Campaninan A',
         'Campanian black glazed pottery B': 'Ceràmica de Vernís Negre Campaninan B',
         'Campanian black glazed pottery C': 'Ceràmica de Vernís Negre Campaninan C',
         'Post-talaiotic pottery': 'Ceràmica Posttalaiòtica',
         'Iberian common ware': 'Ceràmica comuna ibèrica',
         'Italic common ware': 'Ceràmica Comuna Itàlica',
         'Punic common ware': 'Ceràmica Comuna Púnica',
         'Catalan coast grey pottery': 'Ceràmica grisa de la costa catalana',
         'Punic Ebusitan common ware': 'Ceràmica Comuna Punicoebusitana',
         'Ebusitan black glaze pottery': 'Ceràmica de Vernís Negre Ebusitana',
         'Massalian amphora': 'Àmfora massaliota'
         }

    productions = None

    if lang == 'both':
        productions = p
    elif lang == 'eng':
        productions = list(p.keys())
    elif lang == 'cat':
        productions = list(p.values())

    return productions


#######################################################################################################################


def get_early_roman(lang='both'):
    """Access Early Roman period productions

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Early Roman period productions. If lang='both', return dict, else return a list
    """
    p = {'Tarraconense amphora': 'Àmfora Tarraconense',
         'Salazones amphora': 'Àmfora de Salaons',
         'Gaulish amphora': 'Àmfora gala',
         'Terra Sigillata - Gaulish': 'Terra Sigillata - Gala',
         'North African amphora': 'Àmfora Nord-Africana',
         'Thin walled pottery - Italic': 'Ceràmica de parets fines itàlica',
         'Thin walled pottery - Ebusitan': 'Ceràmica de parets fines ebusitana',
         'Roman cooking ware': 'Ceràmica de Cuina Romana',
         'Terra Sigillata - Classic': 'Terra Sigillata - Clàssic',
         'Thin walled pottery': 'Ceràmica de parets fines',
         'Roman Ebusitan common ware': 'Ceràmica Comuna Romana Ebusitana',
         'Tarraconense Maresme amphora': 'Àmfora Tarraconense - Maresme',
         'Hispanic Amph- South Iberian Coast': None,
         'Hispanic Amph- Guadalquivir Valley': 'Àmfora de la vall del Guadalquivir',
         'Ebusitan Amph. - Roman': None
         }

    productions = None

    if lang == 'both':
        productions = p
    elif lang == 'eng':
        productions = list(p.keys())
    elif lang == 'cat':
        productions = list(p.values())

    return productions

#######################################################################################################################


def get_late_roman(lang='both'):
    """Access Late Roman period productions

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Late Roman period productions. If lang='both', return dict, else return a list
    """
    p = {'Late Roman amphorae (LRA)': 'Late Roman amphorae (LRA)',
         'Terra Sigillata - Hispanic': 'Terra Sigillata - Hispànica',
         'Terra Sigillata - African A': 'Terra Sigillata - Africana A',
         'Terra Sigillata - African C': 'Terra Sigillata - Africana C',
         'Terra Sigillata - African D': 'Terra Sigillata - Africana D',
         'DSP Derivee de sigille paleochretienne': 'DSP Derivee de sigille paleochretienne',
         'Roman common ware': 'Ceràmica Comuna Romana',
         'Roman oil lamp': 'Llàntia romana',
         'Late Roman C': 'Late Roman C',
         'Late Roman cooking ware': 'Late Roman cooking ware'
         }

    productions = None

    if lang == 'both':
        productions = p
    elif lang == 'eng':
        productions = list(p.keys())
    elif lang == 'cat':
        productions = list(p.values())

    return productions


#######################################################################################################################


def get_islamic(lang='both'):
    """Access Islamic period productions

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Islamic period productions. If lang='both', return dict, else return a list
    """
    p = {'Islamic medieval common ware': 'Ceràmica Comuna Medieval Islàmica',
         'Islamic medieval glazed pottery': 'Ceràmica Vidrada Medieval Islàmica'
         }

    productions = None

    if lang == 'both':
        productions = p
    elif lang == 'eng':
        productions = list(p.keys())
    elif lang == 'cat':
        productions = list(p.values())

    return productions


#######################################################################################################################


def get_misc_types(lang='both'):
    """Access types that we usually include with productions (but might not be officially designated FabricTypeNames

    Parameters
    ----------
    lang : {'both', 'eng', 'cat'}
        The language you need for the output

    Returns
    -------
    productions : dict, list
        Islamic period productions. If lang='both', return dict, else return a list
    """
    materials_dict = {
        'Unworked clay': 'argila cuita',
        'brick': 'maó',
        'other': 'altre',
        'other constr': 'altre material de construcció',
        'tile': 'teula',
        'unknown': 'indeterminada',
        'vessel': 'altre vaixell'
    }

    material_names = None

    if lang == 'both':
        material_names = materials_dict
    elif lang == 'eng':
        material_names = list(materials_dict.keys())
    elif lang == 'cat':
        material_names = list(materials_dict.values())

    return material_names


#######################################################################################################################
