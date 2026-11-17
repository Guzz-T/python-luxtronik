window.KEYS = {
  {% for key in keys %}"{{key.value}}"{{": {"}}
      "key": "{{key.value}}",
      "requirement": "{{key.requirement}}",
      "default_value": "{{key.default_value}}",
      "description": "{{key.description}}"
  {{"}"}}{% if not loop.last %},
  {% endif %}{% endfor %}
};
