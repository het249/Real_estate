/*
$('#submit_property').click(function (e) {
    debugger;
    e.preventDefault();
    $("#submit_property").button('loading');

    var data = {
        Name: $('#property_name').val(),
        Description: $('#property_description').val(),
        Bedrooms: $('#property_bedrooms').val(),
        Bathrooms: $('#property_bathrooms').val(),
        Kitchen: $('#property_kitchen').val(),
        Livingarea: $('#property_livingarea').val(),
        Gardenarea: $('#property_gardenarea').val()
    };

    var formData = new FormData();

    formData.append("data", JSON.stringify(data));

    var totalFiles = document.getElementById('property_images').files.length;
    
    for(var i = 0; i < totalFiles; i++){
        var file = document.getElementById('property_images').files[i];
        formData.append("httpPostedFileBase", file);
    }
    $.ajax({
        type: "POST",
        url: '/publish_property_rpc',
        data: formData,
        dataType: 'json',
        contentType: false,
        processData: false,
        success: function (response) {
            if (response != null) {
                console.log(response);                 
            }
            else {
                alert('No Response...!');
            }
        },
        error: function (error) {
            alert("error");
        }
    });
    
});
*/

async function publish_property_rpc() {
    debugger;
    var data = {
        Name: document.getElementById("property_name").value,
        Description: document.getElementById("property_description").value,
        Bedrooms: document.getElementById("property_bedrooms").value,
        Bathrooms: document.getElementById("property_bathrooms").value,
        Kitchen: document.getElementById("property_kitchen").value,
        Livingarea: document.getElementById("property_livingarea").value,
        Gardenarea: document.getElementById("property_gardenarea").value,
        Files: document.getElementById('property_images').files
    };

    var formData = new FormData();

    formData.append("data", data);

    var totalFiles = document.getElementById('property_images').files.length;
    var files = document.getElementById('property_images').files;
    if(files.length){
        formData.append("httpPostedFileBase", files);
        console.log(files)
    }

    await fetch('/publish_property_rpc', {
      method: "POST",
      header: {'Content-Type': 'multipart/form-data'},
      body: JSON.parse(data)
    })
    .then((response) => response.json())
    .then((data) => {
        console.log("File uploaded successfully");
        console.log(data);
    })
    .catch((error) => {
        console.error(error);
    });

}