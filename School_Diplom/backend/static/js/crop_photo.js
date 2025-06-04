document.addEventListener('DOMContentLoaded', function () {
  var image = document.getElementById('image');
  var cropper;

  $('#modalCrop').on('shown.bs.modal', function () {
    cropper = new Cropper(image, {
      aspectRatio: 325 / 300,
      viewMode: 1,
      autoCropArea: 1,
      responsive: true,
    });
  }).on('hidden.bs.modal', function () {
    cropper.destroy();
    cropper = null;
  });

  document.getElementById('crop').addEventListener('click', function () {
    var canvas = cropper.getCroppedCanvas({
      width: 325,
      height: 300,
    });

    canvas.toBlob(function (blob) {
      var reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = function () {
        var base64data = reader.result;
        document.getElementById('image').src = base64data;
        $('#modalCrop').modal('hide');
        document.getElementById('cropped-image').value = base64data;
      };
    });
  });

  window.readURL = function (input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $('#image').attr('src', e.target.result);
        $('#modalCrop').modal('show');
      }
      reader.readAsDataURL(input.files[0]);
    }
  };

  document.getElementById('edit-profile-form').addEventListener('submit', function (event) {
    var croppedImage = document.getElementById('cropped-image').value;
    if (!croppedImage) {
      event.preventDefault();
      alert("Пожалуйста, обрежьте изображение перед сохранением.");
    }
  });
});