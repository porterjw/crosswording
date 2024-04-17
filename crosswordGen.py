import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

iam_client = boto3.client('iam')
role = iam_client.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

# Hub Model configuration. https://huggingface.co/models
hub = {
	'HF_MODEL_ID':'azugarini/clue-instruct-llama-13b',
	'SM_NUM_GPUS': json.dumps(1)
}

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
	image_uri=get_huggingface_llm_image_uri("huggingface",version="1.4.2"),
	env=hub,
	role=role, 
)
# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
	initial_instance_count=1,
	instance_type="ml.t2.2xlarge",
	container_startup_health_check_timeout=300,
  )

# send request
predictor.predict({
	"inputs": "Hey my name is Julien! How are you?",
})

