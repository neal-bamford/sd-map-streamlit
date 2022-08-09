import uuid


class Cell:
  def __new__(cls, *args, **kwargs):
    _cell = super().__new__(cls)
    _cell.__init__()
    return _cell

  def __init__(self):
    self.id = str(uuid.uuid4())[:4]
    self.image_content = None
    self.image_width = 6
    self.image_alignemt = 'left'
    self.text_content = None
    self.text_alignemtn = 'left'
    
    
    print(self.id)
    
  def id() ->str:
    return id
  
  def set_image_content(self, image_content, image_alignment, image_width):
    self.text_content    = None
    self.image_content   = image_content
    self.image_alignment = image_alignment
    self.image_width     = image_width
  
  def is_image_content(self):
    return self.image_content != None
    
  def set_text_content(self, text_content, text_alignment):
    self.image_content  = None
    self.text_content   = text_content
    self.text_alignment = text_alignment
    
  def is_text_content(self):
    return self.text_content != None

  def get_content(self) -> str:
    
    ret_val = "No Content Set"
    
    if self.is_image_content():
      ret_val = f"image-{self.image_content}:alignment-{self.image_alignment}:width-{self.image_width}"
    elif self.is_text_content():
      ret_val = f"text-{self.text_content}:alignment-{self.text_alignment}"

    return ret_val
      
    