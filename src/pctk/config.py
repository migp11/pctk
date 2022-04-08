
phase_grouping = { 
    "Ki67_positive_premitotic": "live",  
    "Ki67_positive_postmitotic": "live", 
    "Ki67_positive": "live", 
    "Ki67_negative": "live", 
    "G0G1_phase": "live", 
    "G0_phase": "live", 
    "G1_phase": "live", 
    "G1a_phase": "live", 
    "G1b_phase": "live", 
    "G1c_phase": "live", 
    "S_phase": "live", 
    "G2M_phase": "live", 
    "G2_phase": "live", 
    "M_phase": "live", 
    "live": "live", 
    "apoptotic": "apoptotic",  
    "necrotic_lysed": "necrotic", 
    "necrotic_swelling": "necrotic"
    }

phases_dict = {
    0: "Ki67_positive_premitotic",
    1: "Ki67_positive_postmitotic",
    2: "Ki67_positive",
    3: "Ki67_negative",
    4: "G0G1_phase",
    5: "G0_phase",
    6: "G1_phase",
    7: "G1a_phase",
    8: "G1b_phase",
    9: "G1c_phase",
    10: "S_phase",
    11: "G2M_phase",
    12: "G2_phase",
    13: "M_phase",
    14: "live",
    100: "apoptotic",
    101: "necrotic_swelling",
    102: "necrotic_lysed",
    103: "necrotic",
    104: "debris"
    }


default_pov_colors = { 
    'live':{
            'cytoplasm': [.25, 1, .25],
            'nuclear':   [0.03, 0.125, 0],
            'finish':    [0.05, 1, 0.1]
        }, 
    'apoptotic': {
            'cytoplasm': [ 1, 0, 0],
            'nuclear':   [0.125, 0, 0],
            'finish':    [0.05, 1, 0.1]

         }, 
    'necrotic': {
            'cytoplasm': [1, 0.5412, 0.1490],
            'nuclear':   [0.125, 0.06765, 0.018625],
            'finish':    [0.01, 0.5, 0.1]
        } 
    }
