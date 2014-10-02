$('#ratings').raty({
  path: function() {
    return this.getAttribute('data-path');
  }
});