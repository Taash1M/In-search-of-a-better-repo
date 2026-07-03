---
name: reference-gpt-image-not-on-bedrock
description: AWS Bedrock does NOT host GPT-Image; the AWS-native text-to-image model is Amazon Nova Canvas (or Titan Image Generator v2 / Stability). Use Nova Canvas for AWS-native infographics.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

**GPT-Image / GPT-Image-2 is an OpenAI/Azure model — it is NOT available on AWS Bedrock.** When a
task asks for a "text-to-image model on AWS" or "latest GPT-image on AWS", the AWS-native equivalent is
**Amazon Nova Canvas** (latest; alternatives: **Amazon Titan Image Generator v2**, **Stability** models).

**How to apply:** For AWS-hosted infographics/illustrations, deploy/enable **Nova Canvas** on Bedrock
(us-east-2 for the PLM project), tag it with PLM tagging (`Project=FLK-PLM-Drawings-AI`, add to Resource
Group `FLK-PLM-Drawings-AI`). Nova Canvas returns PNGs at fixed supported dimensions (composite into A4
in the DOCX builder, don't generate at A4 directly). The existing Azure GPT-Image-2 pipeline (used for
production PLM infographics) is a **cross-cloud** call — only use it from AWS work under explicit
cross-cloud export sign-off; default to Nova Canvas to keep an AWS project self-contained.

Caught during the [[project-aws-twin]] plan review (a draft promised "GPT-image on AWS Bedrock").
Related: [[reference_gpt_image2]] (the Azure GPT Image 2 setup).
