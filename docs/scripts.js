// ==============================================================================
// SPDX-License-Identifier: MIT
//
// AI-Generated Code Notice:
// Generated with: Gemini (Google)
// Date: 2026-11-11
// Human Review: Reviewed, adapted, and verified by Guzz-T
//
// Disclaimer:
// This script is provided "AS IS", without warranty of any kind. Review before
// execution in your local or production environment.
// ==============================================================================

// Combine all data sources
let data = [
  ...window.CALCULATION,
  ...window.PARAMETER,
  ...window.VISIBILITY,
  ...window.INPUT,
  ...window.HOLDING
];

const tableBody = document.querySelector("#table tbody");
const filterFields = [...document.querySelectorAll("thead input")];

/**
 * Checks if a specific version meets the condition string stored in the dataset.
 *
 * @param {string} filterVersion - The concrete version typed by the user (e.g., "1.5").
 * @param {string} itemVersionExpression - The condition string from the dataset (e.g., ">=1.0, <2.0").
 * @returns {boolean} True if the filter version satisfies all dataset conditions.
 */
function checkVersionCondition(filterVersion, itemVersionExpression) {
    // Remove all whitespaces and split the dataset expression by comma OR semicolon
    const conditions = itemVersionExpression.replace(/\s+/g, '').split(/[,;]/);

    // Split the user's filter version into an array of numbers (e.g., "1.5" ->)
    const v1 = String(filterVersion).split('.').map(Number);

    for (const condition of conditions) {
        if (!condition) continue;

        // Regex to extract the optional operator and the target version number from the dataset
        const match = condition.match(/^(>=|<=|>|<|==|=)?([0-9.]+)/);
        if (!match) continue;

        // If the dataset has no operator (e.g., just "1.0"), default to exact match "=="
        const operator = match[1] || '==';
        const v2 = match[2].split('.').map(Number);

        // Component-by-component version comparison
        // Returns -1 if v1 < v2, 1 if v1 > v2, 0 if they are identical
        let comparisonResult = 0;
        for (let i = 0; i < Math.max(v1.length, v2.length); i++) {
            const num1 = v1[i] || 0;
            const num2 = v2[i] || 0;
            if (num1 < num2) { comparisonResult = -1; break; }
            if (num1 > num2) { comparisonResult = 1; break; }
        }

        // Validate if the user's version violates the dataset's condition
        if (operator === '>=' && comparisonResult < 0) return false;
        if (operator === '<=' && comparisonResult > 0) return false;
        if (operator === '>'  && comparisonResult <= 0) return false;
        if (operator === '<'  && comparisonResult >= 0) return false;
        if ((operator === '==' || operator === '=') && comparisonResult !== 0) return false;
    }
    return true;
}

/**
 * Filter function evaluated against each dataset item.
 *
 * @param {Object} item - The current row/data object being evaluated.
 * @returns {boolean} True if the item matches all filter criteria.
 */
function matchesFilters(item) {
  const fields = {
      category: f_category.value.trim(),
      index: f_index.value.trim(),
      name: f_name.value.trim(),
      lsb: f_lsb.value.trim(),
      width: f_width.value.trim(),
      class: f_class.value.trim(),
      unit: f_unit.value.trim(),
      writeable: f_writeable.value.trim(),
      description: f_description.value.trim()
  };

  // 1. Process standard text fields using regular expressions
  for (const key in fields) {
      const filterValue = fields[key];
      if (!filterValue) continue;

      try {
          const regex = new RegExp(filterValue, "i");
          if (!regex.test(String(item[key]))) return false;
      } catch (e) {
          return false;
      }
  }

  // 2. Process the version field (User types "1.5", Data has ">=1.0, <2.0")
  const versionFilter = f_version.value.trim();
  if (versionFilter) {
      // If the item has no version expression defined, it will be displayed
      if (!item.version) return true;

      // Pass the user's input as the first argument, and the dataset's expression as the second
      if (!checkVersionCondition(versionFilter, item.version)) return false;
  }

  return true;
}

// hide or show columns
function activateColumnToggle() {
  document.querySelectorAll('#columnToggle input').forEach(cb => {
      cb.addEventListener('change', () => {
          const colIndex = parseInt(cb.dataset.col);

          document.querySelectorAll(`thead tr th:nth-child(${colIndex})`)
              .forEach(th => th.classList.toggle('hide-col', !cb.checked));

          document.querySelectorAll(`tbody tr td:nth-child(${colIndex})`)
              .forEach(td => td.classList.toggle('hide-col', !cb.checked));
      });
  });
}

// initial visibility
function applyInitialColumnVisibility() {
  document.querySelectorAll('#columnToggle input').forEach(cb => {
      const colIndex = parseInt(cb.dataset.col);

      if (!cb.checked) {
          document.querySelectorAll(`thead tr th:nth-child(${colIndex})`)
              .forEach(th => th.classList.add('hide-col'));

          document.querySelectorAll(`tbody tr td:nth-child(${colIndex})`)
              .forEach(td => td.classList.add('hide-col'));
      }
  });
}

// Re-render table
function renderTable() {
  tableBody.innerHTML = "";

  data.filter(matchesFilters).forEach(item => {
      const row = document.createElement("tr");
      row.innerHTML = `
      <td>${item.category}</td>
      <td>${item.index}</td>
      <td>${item.name}</td>
      <td>${item.lsb}</td>
      <td>${item.width}</td>
      <td>${item.class}</td>
      <td>${item.unit}</td>
      <td>${item.writeable}</td>
      <td>${item.version}</td>
      <td class="description">${item.description}</td>
      `;
      tableBody.appendChild(row);
  });

  applyInitialColumnVisibility();
}

// activate filter event
filterFields.forEach(f => f.addEventListener("input", renderTable));

// set creation-date
document.getElementById("createdInfo").textContent =
    `Generated automatically on ${window.META.createdOn}`;
// set version
document.getElementById("versionInfo").textContent =
    `Build version: ${window.META.version}`;



// initial rendering
activateColumnToggle();
renderTable();
