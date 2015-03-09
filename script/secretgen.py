import base64
import uuid
 
print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)