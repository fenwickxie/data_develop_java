package com.example.dataplatform.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class SecurityUserService implements UserDetailsService {

    private final String demoUsername;
    private final String encodedPassword;
    private final PasswordEncoder encoder = new BCryptPasswordEncoder();

    public SecurityUserService(
            @Value("${security.demo-user.username}") String demoUsername,
            @Value("${security.demo-user.password}") String demoPassword
    ) {
        this.demoUsername = demoUsername;
        this.encodedPassword = encoder.encode(demoPassword);
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        if (!demoUsername.equals(username)) {
            throw new UsernameNotFoundException("User not found");
        }
        return User
                .withUsername(demoUsername)
                .password(encodedPassword)
                .roles("USER")
                .build();
    }

    public boolean matches(String rawPassword) {
        return encoder.matches(rawPassword, encodedPassword);
    }
}
