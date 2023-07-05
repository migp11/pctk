
phase_grouping = { 
    "Ki67_positive_premitotic": "alive",  
    "Ki67_positive_postmitotic": "alive", 
    "Ki67_positive": "alive", 
    "Ki67_negative": "alive", 
    "G0G1_phase": "alive", 
    "G0_phase": "alive", 
    "G1_phase": "alive", 
    "G1a_phase": "alive", 
    "G1b_phase": "alive", 
    "G1c_phase": "alive", 
    "S_phase": "alive", 
    "G2M_phase": "alive", 
    "G2_phase": "alive", 
    "M_phase": "alive", 
    "live": "alive", 
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

default_cell_colors = {
    'alive': '#75db75', 
    'apoptotic': '#ef4242', 
    'necrotic': '#97723d'}


default_pov_colors = { 
    'alive':{
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


DEFAULT_XML = """<?xml version="1.0" encoding="UTF-8"?>

<povwriter_settings>
	<camera>
		<distance_from_origin units="micron">750</distance_from_origin>
		<xy_angle>3.92699081699</xy_angle> <!-- 5*pi/4 -->
		<yz_angle>1.0471975512</yz_angle> <!-- pi/3 --> 
	</camera>

	<options>
		<use_standard_colors>true</use_standard_colors>
		<nuclear_offset units="micron">0.1</nuclear_offset> <!-- how far to clip nuclei in front of cyto --> 
		<cell_bound units="micron">500</cell_bound> <!-- only plot if |x| , |y| , |z| < cell_bound -->
		<threads>1</threads>
	</options>

	<save> 
		<folder>./test/output/</folder>
		<filebase>output</filebase> 
		<time_index>0</time_index> 
	</save>
	
	<clipping_planes> <!-- done --> 
		<clipping_plane>0,-1,0,0</clipping_plane>
		<clipping_plane>-1,0,0,0</clipping_plane>
		<clipping_plane>0,0,1,0</clipping_plane>
	</clipping_planes>
	
	<!-- if using standard coloring (above), these will be used --> 
	<!-- otherwise, the code will look for a user-defined color/finish function -->  <!-- done --> 
	<cell_color_definitions>
		<!-- each cell's type will be used to choose a coloring scheme for alive, apoptotic, or necrotic -->
		<!-- If the cell's type is not recognized, the standard coloring function will default to 0 --> 
		<cell_colors type="0">
			<alive>
				<cytoplasm>.25,1,.25</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.03,0.125,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</alive>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> <!-- ambient,diffuse,specular -->
			</necrotic>
		</cell_colors>
		
		<cell_colors type="1">
			<alive>
				<cytoplasm>0.25,0.25,1</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.03,0.03,0.125</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</alive>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> <!-- ambient,diffuse,specular -->
			</necrotic>
		</cell_colors>
	
	</cell_color_definitions>

</povwriter_settings>
"""