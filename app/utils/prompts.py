keep_identity_prompt = """
CRITICAL IDENTITY PRESERVATION:
- Keep the original person's face unchanged and realistic
- Preserve facial structure, skin tone, eye color, and all facial features exactly
- Maintain skin texture and pores; avoid plastic smoothing
- Keep natural proportions and face geometry
- Preserve hair style and hair color exactly
- Same person as reference - 99% likeness, no facial changes
- Keep identity identical across all edits
"""

try_on_prompt = f"""
Task: Outfit the person from the first image in the clothing from the second image.

{keep_identity_prompt}

Specific clothing requirements:
- Replace ONLY the clothing with the garment from the second image
- Ensure realistic fit, draping, and fabric behavior on the person's body
- Match the person's exact pose and body position
- Preserve natural shadows and lighting
- Keep background, lighting, and camera angle unchanged
- Do not add accessories, jewelry, or any items not in the clothing image

Output a photorealistic result showing how this specific clothing would look when worn by this specific person, with the face remaining completely identical to the original.
"""
