from image.color import has_white_pix
from image.match_tem import match_static,match_dynamic
from utili.tem_manager import load_all_templates
from utili.path_manager import TEM_DIR

rio_dict={
    "nickname":[570,409,20,10],
    "escape":[473, 640, 27, 12]
}

tem_dict = load_all_templates(template_dir=TEM_DIR)



def det_nickname(frame):
    return has_white_pix(frame,rio_dict["nickname"])

def det_escape(frame):
    return match_static(frame,rio_dict["escape"],tem_dict["escape"])


