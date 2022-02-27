var inputs = document.getElementsByTagName("input");

console.log(inputs);

for (let i = 0; i < inputs.length; i++) {
  console.log("coucou");
  if (inputs[i].type == "checkbox") {
    console.log("hello");
  }
}

function requestedResourcesUpdate(checkbox) {
  console.log(checkbox);
  fetch("/requested-resources-update", {
    method: "POST",
    body: JSON.stringify({
      resource_id: checkbox.value,
      selected: checkbox.checked,
    }),
  });
}

console.log("checkboxes");
console.log(inputs);

function requestResources() {
  fetch("/request-resources", {
    method: "POST",
  }).then((_res) => {
    window.location.href = "/";
  });
}

function freeResource() {
  fetch("/free-resources", {
    method: "POST",
  }).then((_res) => {
    window.location.href = "/";
  });
}
