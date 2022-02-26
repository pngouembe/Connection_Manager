function buttonPress(resource_id){
    alert("Hello " + resource_id)
    fetch("/request", {
        method: "POST",
        body: JSON.stringify({ resource_id: resource_id }),
      }).then((_res) => {
        window.location.href = "/";
      });
}