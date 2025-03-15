from openai import OpenAI


class China:
    def __init__(self):
        pass

    def inference(self, model_id: str, prompt: str) -> str:
        completion = OpenAI(
            api_key="sk-lHKZ5qJaGU3axOPVnCJSGMdiYep04VRSwCMB311rnCE9Fh19",
            base_url="https://api.moonshot.cn/v1",
        )
        result = completion.chat.completions.create(
            model=model_id,
            # model="moonshot-v1-128k",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return result.choices[0].message.content
