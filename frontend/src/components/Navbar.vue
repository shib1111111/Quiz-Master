<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">MyApp</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <!-- Render links based on the role prop -->
          <li class="nav-item" v-if="role === 'admin'">
            <a class="nav-link" href="#">Admin Dashboard</a>
          </li>
          <li class="nav-item" v-if="role === 'user'">
            <a class="nav-link" href="#">User Dashboard</a>
          </li>
          <li class="nav-item">
            <button class="btn btn-link nav-link" @click="$emit('logout')">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'Navbar',
    props: {
      role: {
        type: String,
        required: true,
      },
    },
  };
  </script>
  