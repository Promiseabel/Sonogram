const SignInForm = {
    template: `
    <div>
        <h2 class="welcomeheaders">Sign In</h2>
        <form @submit.prevent="signIn">
            <div>
                <label for="username">Username</label>
                <input type="text" id="username" v-model="username" required>
            </div>
            <div>
                <label for="password">Password</label>
                <input type="password" id="password" v-model="password" required>
            </div>
            <button type="submit">Sign In</button>
            <button @click="$emit('change-screen', 'welcome')">Back</button>
        </form>
        <div v-if="errorMessage">{{ errorMessage }}</div>
    </div>
    `,
    data() {
        return {
            username: '',
            password: '',
            errorMessage: ''
        }
    },
    methods: {
        signIn() {
        const credentials = {
            username: this.username,
            password: this.password
        };

        axios.post('/signin', credentials)
            .then(response => {

                console.log('Signed in successfully', response.data);

                this.$emit('change-screen', 'home-page');
                

            })
            .catch(error => {
                if (error.response && error.response.status === 401) {
                    this.errorMessage = 'Invalid username or password.';
                } else {
                    this.errorMessage = 'An error occurred. Please try again later.';
                }
                console.error('Sign in error', error.response);
            });
        }
    }
};

const SignUpForm = {
    template: `
    <div>
        <h2 class="welcomeheaders">Sign Up</h2>
        <form @submit.prevent="signUp">
            <div>
                <label for="username">Username</label>
                <input type="text" id="username" v-model="username" required>
            </div>
            <div>
                <label for="password">Password</label>
                <input type="password" id="password" v-model="password" required>
            </div>
            <div>
                <label for="confirmPassword">Confirm New Password</label>
                <input type="password" id="confirmPassword" v-model="confirmPassword" required>
            </div>
            <div>
                <label for="email">Email Address</label>
                <input type="email" id="email" v-model="email" required>
            </div>
            <div>
                <label for="bio">Bio</label>
                <textarea id="bio" v-model="bio"></textarea>
            </div>
            <div>
                <label for="profilePicture">Profile Picture</label>
                <input type="file" id="profilePicture" @change="validateImage" required>
            </div>
            <button type="submit">Create Account</button>
            <button @click="$emit('change-screen', 'welcome')">Back</button>
        </form>
        <div v-if="errorMessage">{{ errorMessage }}</div>
    </div>
    `,
    data() {
        return {
            username: '',
            password: '',
            confirmPassword: '',
            email: '',
            bio: '',
            profilePicture: null,
            errorMessage: ''
        }
    },
    methods: {
        signUp() {
        
        if (!this.validateUsername() || !this.validatePassword() || !this.validateEmail() || !this.validateBio()) {
            // If any validation fails, stop the sign-up process
            return;
        }

        let formData = new FormData();
        formData.append('username', this.username);
        formData.append('password', this.password);
        formData.append('email_address', this.email);
        formData.append('bio', this.bio);
        formData.append('profile_picture', this.profilePicture);

        axios.post('/signup', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(response => {
            console.log(response.data);
            this.$emit('change-screen', 'home-page');

        }).catch(error => {
            this.errorMessage = error.response.data.error || 'An error occurred during sign-up.';
        });
        },    
        validateUsername() {
            if (this.username.length > 25) {
                this.errorMessage = 'Username cannot be more than 25 characters.';
                return false;
            }
            return true;
        },
        validatePassword() {
            if (this.password !== this.confirmPassword) {
                this.errorMessage = 'Passwords do not match.';
                return false;
            }
    
            const strongPasswordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
            if (!this.password.match(strongPasswordPattern)) {
                this.errorMessage = 'Password must be at least 8 characters long, contain a mix of upper and lower case letters, at least one number, and at least one special character.';
                return false;
            }
            return true;
        },
        validateEmail() {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!this.email.match(emailPattern) || this.email.length > 255) {
                this.errorMessage = 'Please provide a valid email address not more than 255 characters.';
                return false;
            }
            return true;
        },
        validateBio() {
            if (this.bio.length > 255) {
                this.errorMessage = 'Bio cannot be more than 255 characters.';
                return false;
            }
            return true;
        },
        validateImage(event) {
            const file = event.target.files[0];
            this.profilePicture = file;
            
            const acceptedTypes = ['image/png', 'image/jpeg', 'image/jpg'];

            if (!acceptedTypes.includes(file.type)) {
                this.errorMessage = 'Please select an image file of type PNG, JPG, or JPEG.';
                return;
            }
            
            // Basic validation for file size (let's say the limit is 5MB)
            if (file.size > 5242880) {
                this.errorMessage = 'The image size should be less than 5MB.';
                return;
            }

        }
    }
};

const WelcomeScreen = {
    template: `
    <div class="content">
        <div class="welcomeheaders">Welcome to Sonogram</div>
        <div class="buttons">
            <button @click="$emit('change-screen', 'sign-in')">Sign In</button>
            <button @click="$emit('change-screen', 'sign-up')">Sign Up</button>
        </div>
    </div>
    `
};

Vue.component('audio-item', {
    props: ['audio'],
    template: `
      <div class="audio-item">
        <button class="username-link" @click="goToUserProfile(audio.user_id)">{{ audio.username }}</button>
        <div class="audio-image" @click="playAudio(audio.audio_id)">
          <img :src="'static/imagefiles/' + audio.profile_picture" alt="User profile picture">
          <button class="play-btn">{{ isPlaying ? 'Pause' : 'Play' }}</button>
        </div>
        <p class="title">{{ audio.title }}</p>
      </div>provide the css
    `,
    data() {
      return {
        isPlaying: false
      };
    },
    methods: {
      playAudio(audioId) {
        // Play or pause the audio
        this.isPlaying = !this.isPlaying;
        this.$emit('audio-selected', audioId, this.isPlaying);
      },
      goToUserProfile(userId){
        this.$emit('change-screen', 'user-profile', userId);
      }
    }
});

const HomePage = {
    data() {
      return {
        audios: [],
        audioReplies: [], // This will hold the list of audios
        currentAudio: null,
        isPlaying: false,
        showUploadForm: false,
        title: '',
        audioFile: null
      };
    },
    created() {
      // Fetch the audios from the backend
      axios.get('/audios').then(response => {
        this.audios = response.data.audios;
      });
    },
    methods: {
      selectAudio(audioId, isPlaying) {
        // Update the currently playing audio and fetch its replies
        this.isPlaying = isPlaying;
        if (isPlaying) {
          this.currentAudio = this.audios.find(audio => audio.audio_id === audioId);
          // Fetch replies for the current audio
          axios.get('/audios/' + audioId).then(response => {
            this.audioReplies = response.data.replies ? response.data.replies : [];
          });
        } else {
          this.currentAudio = null;
          this.audioReplies = [];
        }
      },
      selectAudioReply(audioId, isPlaying) {
        // Update the currently playing audio and fetch its replies
        this.isPlaying = isPlaying;
      },
      signOut() {
        axios.delete('/signout');
        this.$emit('change-screen', 'welcome');
      },
      handleScreenChange(screen, userId) {
        // This method would emit an event to the root instance
        this.$emit('change-screen', screen, userId);
      },
      goToMyProfile() {
        axios.get('/signin').then(response => {
            this.$emit('change-screen', 'user-profile',response.data.user_id);
        }).catch(error => {
            console.error("Not Signed in:", error);
            this.$emit('change-screen', 'welcome');
        });
      },
      handleFileChange(event) {
        if (event.target.files.length > 0) {
            const file = event.target.files[0];
            const acceptedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
        
            if (!acceptedTypes.includes(file.type)) {
              this.errorMessage = 'Please select an audio file of type MPEG, MP3 or WAV.';
              return;
            }
        
            if (file.size > 5242880) { // 5MB
              this.errorMessage = 'The audio file size should be less than 5MB.';
              return;
            }
        
            this.audioFile = file;
            this.errorMessage = ''; // Clear any previous error message
        }
      },
      uploadAudio() {
        
        if (!this.title || !this.audioFile) {
            this.errorMessage = "Please fill in all fields.";
            return;
          }
        
          if (this.title.length > 255) {
            this.errorMessage = "Title cannot be more than 255 characters.";
            return;
          }
        
          const formData = new FormData();
          formData.append('title', this.title);
          formData.append('audio_file', this.audioFile);
          axios.get('/signin').then(response => {
            axios.post('users/' + response.data.user_id, formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              }).then(() => {
                console.log('Audio uploaded successfully');
                this.showUploadForm = false;
                this.title = '';
                this.audioFile = null;
                this.errorMessage = ''; // Clear any error messages
                axios.get('/audios').then(response => {
                    this.audios = response.data.audios;
                  });
                // Optionally, refresh the list of audios
              }).catch(error => {
                console.error('Upload error', error);
                this.errorMessage = 'Failed to upload audio. Please try again.';
              });
        }).catch(error => {
            console.error("Not Signed in:", error);
            this.$emit('change-screen', 'welcome');
        });
          
      },
      likeAudio(audioId){
        //Add Functionality
      }
    },
    template: `
      <div class="content">
        <header class="header">
          <div class="header-item" @click="signOut">Sign Out</div>
          <div class="header-item" id="logo">Sonogram</div>
          <div class="header-item" @click="goToMyProfile">My Profile</div>
        </header>
        <div class="upload-button">
            <!-- Upload button that shows the form when clicked -->
            <button @click="showUploadForm = !showUploadForm" class="upload-circle">+</button>
        </div>
        
        <!-- Upload form -->
        <div v-if="showUploadForm" class="upload-form">
            <form @submit.prevent="uploadAudio">
            <div>
                <label for="title">Title</label>
                <input type="text" id="title" v-model="title" required>
            </div>
            <div>
                <label for="audioFile">Audio File</label>
                <input type="file" id="audioFile" @change="handleFileChange" accept="audio/*" required>
            </div>
            <button type="submit">Upload Audio</button>
            </form>
        </div>
        <div class="audio-list">
          <audio-item v-for="audio in audios" :audio="audio" @audio-selected="selectAudio" @change-screen="handleScreenChange"></audio-item>
        </div>
        <div class="current-audio" v-if="currentAudio">
          <!-- Show the current audio details and controls here -->
          <div class="audio-controls">
            <span>{{ currentAudio.title }}</span>
            <button @click="likeAudio(currentAudio.audio_id)">Like</button>
            <!-- Add more controls as needed -->
          </div>
          <div class="audio-list">
            <audio-item v-for="audio in audioReplies" :audio="audio" @audio-selected="selectAudioReply" @change-screen="handleScreenChange"></audio-item>
          </div>
        </div>
      </div>
    `
  };

const UserProfile = {
    props: ['userId'],
    data() {
      return {
        userProfile: null,
        audios: [],
        audioReplies: [],
        currentAudio: null,
        isPlaying: false,
        signedInUserId: ''
      };
    },
    computed: {
      isMyProfile() {
        return this.userProfile && this.userId === this.signedInUserId;
      }
    },
    created() {
        this.fetchUserProfile(this.userId)
    },
    methods: {
        fetchUserProfile(userId) {
            this.userId = userId;
            axios.get(`/users/${userId}`).then(response => {
            this.userProfile = response.data;
            this.audios = this.userProfile.audios;
            }).catch(error => {
            console.error('Error fetching user profile', error);
            });
            axios.get('/signin').then(response => {
                this.signedInUserId = response.data.user_id;
            }).catch(error => {
                console.error("Not Signed in:", error);
                this.$emit('change-screen', 'welcome');
            });
        },
      selectAudio(audioId, isPlaying) {
        // Update the currently playing audio and fetch its replies
        this.isPlaying = isPlaying;
        if (isPlaying) {
          this.currentAudio = this.audios.find(audio => audio.audio_id === audioId);
          // Fetch replies for the current audio
          axios.get('/audios/' + audioId).then(response => {
            this.audioReplies = response.data.replies ? response.data.replies : [];
          });
        } else {
          this.currentAudio = null;
          this.audioReplies = [];
        }
      },
      signOut() {
        axios.delete('/signout');
        this.$emit('change-screen', 'welcome');
      },
      goToHomePage() {
        this.$emit('change-screen', 'home-page');
      },
      selectAudioReply(audioId, isPlaying) {
        // Update the currently playing audio and fetch its replies
        this.isPlaying = isPlaying;
      },
      handleScreenChange(screen, userId) {
        // This method would emit an event to the root instance
        this.$emit('change-screen', screen, userId);
      },
      goToMyProfile() {
        axios.get('/signin').then(response => {
            this.fetchUserProfile(response.data.user_id);
        }).catch(error => {
            console.error("Not Signed in:", error);
            this.$emit('change-screen', 'welcome');
        });
      },
      goToUpdateForm() {
        axios.get('/signin').then(response => {
            this.$emit('change-screen', 'update-form',response.data.user_id);
        }).catch(error => {
            console.error("Not Signed in:", error);
            this.$emit('change-screen', 'welcome');
        });
      },
      likeAudio(audioId) {
        // Implementation for liking an audio
      }
      // ... other methods ...
    },
    template: `
      <div class="content">
        <header class="header">
          <div class="header-item" @click="signOut">Sign Out</div>
          <div class="header-item" id="logo" @click="goToHomePage">Sonogram</div>
          <div class="header-item" v-if="!isMyProfile" @click="goToMyProfile">My Profile</div>
          <div class="header-item" v-if="isMyProfile" @click="goToUpdateForm">Update Information</div>
        </header>
        <div class="user-info">
          <!-- User's profile picture, bio, and username here -->
          <img class="profilePic" :src="'static/imagefiles/' + userProfile.profile_picture" alt="Profile Picture">
          <h3>Username: {{ userProfile.username }}</h3>
          <p>Bio: {{ userProfile.bio }}</p>
        </div>
        <div class="audio-list">
          <audio-item v-for="audio in audios" :audio="audio" @audio-selected="selectAudio"></audio-item>
        </div>
        <div class="current-audio" v-if="currentAudio">
          <!-- Show the current audio details and controls here -->
          <div class="audio-controls">
            <span>{{ currentAudio.title }}</span>
            <button @click="likeAudio(currentAudio.audio_id)">Like</button>
            <!-- Add more controls as needed -->
          </div>
          <div class="audio-list">
            <audio-item v-for="audio in audioReplies" :audio="audio" @audio-selected="selectAudioReply" @change-screen="handleScreenChange"></audio-item>
          </div>
        </div>
      </div>
    `
  };


const UpdateForm = {
    props: ['userId'],
    template: `
    <div>
        <h2 class="welcomeheaders">Update Information</h2>
        <form @submit.prevent="save">
            <div>
                <label for="username">Username</label>
                <input type="text" id="username" v-model="username" required>
            </div>
            <div>
                <label for="email">Email Address</label>
                <input type="email" id="email" v-model="email" required>
            </div>
            <div>
                <label for="bio">Bio</label>
                <textarea id="bio" v-model="bio"></textarea>
            </div>
            <div>
                <label for="profilePicture">Profile Picture</label>
                <input type="file" id="profilePicture" @change="validateImage" required>
            </div>
            <button type="submit">Save Information</button>
            <button @click="$emit('change-screen', 'user-profile', userId)">Back</button>
        </form>
        <button style="display: block; margin: auto;" @click="showPasswordUpdateForm = !showPasswordUpdateForm">Update Password</button>

        <div v-if="showPasswordUpdateForm">
            <form @submit.prevent="updatePassword">
                <div>
                    <label for="oldPassword">Old Password</label>
                    <input type="password" id="oldPassword" v-model="oldPassword" required>
                </div>
                <div>
                    <label for="newPassword">New Password</label>
                    <input type="password" id="newPassword" v-model="newPassword" required>
                </div>
                <div>
                    <label for="confirmPassword">Confirm New Password</label>
                    <input type="password" id="confirmPassword" v-model="confirmPassword" required>
                </div>
                <button type="submit">Submit New Password</button>
            </form>
        </div>
        <div v-if="errorMessage">{{ errorMessage }}</div>
    </div>
    `,
    data() {
        return {
            username: '',
            email: '',
            bio: '',
            profilePicture: null,
            showPasswordUpdateForm: false,
            oldPassword: '',
            newPassword: '',
            confirmPassword: '',
            errorMessage: ''
        }
    },
    methods: {
        save() {
            if (!this.validateUsername() || !this.validateEmail() || !this.validateBio()) {
                // If any validation fails, stop the sign-up process
                return;
            }

            let formData = new FormData();
            formData.append('username', this.username);
            formData.append('email_address', this.email);
            formData.append('bio', this.bio);
            formData.append('profile_picture', this.profilePicture);

            axios.put('/users/'+this.userId, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }).then(response => {
                console.log(response.data);
                this.$emit('change-screen', 'home-page');

            }).catch(error => {
                this.errorMessage = error.response.data.error || 'An error occurred during save.';
            });
        },    
        validateUsername() {
            if (this.username.length > 25) {
                this.errorMessage = 'Username cannot be more than 25 characters.';
                return false;
            }
            return true;
        },
        validatePassword() {
            const strongPasswordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
            if (!this.newPassword.match(strongPasswordPattern)) {
                this.errorMessage = 'Password must be at least 8 characters long, contain a mix of upper and lower case letters, at least one number, and at least one special character.';
                return false;
            }
            return true;
        },
        validateEmail() {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!this.email.match(emailPattern) || this.email.length > 255) {
                this.errorMessage = 'Please provide a valid email address not more than 255 characters.';
                return false;
            }
            return true;
        },
        validateBio() {
            if (this.bio.length > 255) {
                this.errorMessage = 'Bio cannot be more than 255 characters.';
                return false;
            }
            return true;
        },
        validateImage(event) {
            const file = event.target.files[0];
            this.profilePicture = file;
            
            const acceptedTypes = ['image/png', 'image/jpeg', 'image/jpg'];

            if (!acceptedTypes.includes(file.type)) {
                this.errorMessage = 'Please select an image file of type PNG, JPG, or JPEG.';
                return;
            }
            
            // Basic validation for file size (let's say the limit is 5MB)
            if (file.size > 5242880) {
                this.errorMessage = 'The image size should be less than 5MB.';
                return;
            }

        },
        updatePassword() {
            if (this.newPassword !== this.confirmPassword) {
                this.errorMessage = 'New passwords do not match.';
                return;
            }
    
            if (!this.validatePassword(this.newPassword)) {
                return;
            }
    
            // Submit the password update request
            const payload = {
                oldPassword: this.oldPassword,
                newPassword: this.newPassword,
            };
    
            axios.put(`/users/${this.userId}/update-password`, payload).then(() => {
                axios.delete('/signout');
                this.$emit('change-screen', 'welcome');
            }).catch(error => {
                this.errorMessage = 'Failed to update password. Please try again.';
                console.error('Update password error', error);
            });
        },
    },
    
};

new Vue({
    el: '#app',
    data: {
        currentScreen: '',
        viewingUserId: null,
    },
    components: {
        'welcome': WelcomeScreen,
        'sign-in': SignInForm,
        'sign-up': SignUpForm,
        'home-page': HomePage,
        'user-profile': UserProfile,
        'update-form': UpdateForm
    },
    created(){
        this.checkSignInStatus();
    },
    methods: {
        changeScreen(screen, viewingUserId = null) {
            this.currentScreen = screen;
            this.viewingUserId = viewingUserId;
        },
        checkSignInStatus() {
            // Example HTTP request to check sign-in status
            axios.get('/signin')
                .then(response => {
                    this.currentScreen = 'home-page';
                })
                .catch(error => {
                    console.error("Not Signed in:", error);
                    this.currentScreen = 'welcome';
                });
        }
    }
});