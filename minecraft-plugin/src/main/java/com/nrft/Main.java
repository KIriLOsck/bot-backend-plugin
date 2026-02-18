package com.nrft;

import org.bukkit.event.Listener;
import org.bukkit.event.EventHandler;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.inventory.InventoryOpenEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.player.*;
import org.bukkit.entity.Player;

import java.net.HttpURLConnection;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Random;
import java.util.UUID;
import java.util.logging.Level;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;

import com.google.gson.Gson;

class Answer {
    String serverAnswer;
}

public class Main extends JavaPlugin implements Listener {

    private final HashMap<UUID, Boolean> authenticatedPlayers = new HashMap<>();
    private int code = 0;

    private FileConfiguration config = this.getConfig();
    private Random random = new Random();
    private String endpoint = "";

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("Плагин запущен!");
        this.saveDefaultConfig();
        endpoint = config.getString("backend.endpoint");
    }

    @Override
    public void onDisable() {
        getLogger().info("Плагин остановлен.");
    }

    @EventHandler
    public void onPlayerLoggin(AsyncPlayerPreLoginEvent event) {
        String playerName = event.getName();
        String playerIp = event.getAddress().getHostAddress();
        String checkResult = checkRegister(playerName, playerIp);

        getLogger().log(Level.INFO, "Попытка входа: {0}", playerName + " " + playerIp);

        if ("not exists".equals(checkResult)) {
            event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_WHITELIST, config.getString("whitelist.not_registred"));

        } else if ("pass".equals(checkResult)) {
            authenticatedPlayers.put(event.getUniqueId(), true);
            getServer().broadcastMessage("§3[§a+§3] §f" + playerName);

        } else if ("error".equals(checkResult)) {
            event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_OTHER, config.getString("backend.disable"));

        } else if (!"need login".equals(checkResult)) {
            getLogger().log(Level.INFO, "Ошибка входа: {0}", checkResult);
            event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_OTHER, config.getString("backend.error"));
        }
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        String playerName = player.getName().toLowerCase();

        event.setJoinMessage(null);

        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            authenticatedPlayers.putIfAbsent(player.getUniqueId(), false);
            sendCode(playerName);
            player.sendMessage(config.getString("chat.sent_code"));
        }
    }

    @EventHandler
    public void onPlayerDamage(EntityDamageEvent event) {
        if (event.getEntity() instanceof Player) {
            Player player = (Player) event.getEntity();
            if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
                event.setCancelled(true);
            }
        }
    }

    @EventHandler
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
        }
    }

    @EventHandler
    public void onBlockBreak(BlockBreakEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_break_blocks"));
        }
    }

    @EventHandler
    public void onBlockPlace(BlockPlaceEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_place_blocks"));
        }
    }

    @EventHandler
    public void onInventoryOpen(InventoryOpenEvent event) {
        Player player = (Player) event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_inventory"));
        }
    }

    @EventHandler
    public void onItemDrop(PlayerDropItemEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_throw"));
        }
    }

    @EventHandler
    public void onEntityDamageByPlayer(EntityDamageByEntityEvent event) {
        if (event.getDamager() instanceof Player) {
            Player player = (Player) event.getDamager();
            if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
                event.setCancelled(true);
                player.sendMessage(config.getString("chat.cant_attak"));
            }
        }
    }

    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_use"));
        }
    }

    @EventHandler
    public void onPlayerCommand(PlayerCommandPreprocessEvent event) {
        Player player = event.getPlayer();
        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);
            player.sendMessage(config.getString("chat.cant_command"));
        }
    }

    @EventHandler
    public void onPlayerChat(AsyncPlayerChatEvent event) {
        Player player = event.getPlayer();
        String message = event.getMessage();

        if (Boolean.FALSE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setCancelled(true);

            if (!message.equals(String.valueOf(code))) {
                player.sendMessage(config.getString("chat.cant_chat"));

            } else {
                authenticatedPlayers.replace(player.getUniqueId(), true);
                player.sendMessage(config.getString("chat.success_auth"));
                getServer().broadcastMessage("§3[§a+§3] §f" + player.getName());
            }
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        Player player = event.getPlayer();
        String playerIp = player.getAddress().getAddress().getHostAddress();
        String playerNick = player.getName();

        event.setQuitMessage(null);

        if (Boolean.TRUE.equals(authenticatedPlayers.getOrDefault(player.getUniqueId(), false))) {
            event.setQuitMessage("§3[§4-§3] §f" + playerNick);
            authenticatedPlayers.remove(player.getUniqueId());
            updateLastPlay(playerNick, playerIp);
        }
    }

    private String checkRegister(String playerName, String playerIp) {
        try {
            String data = endpoint + "check?nickname=" + playerName.toLowerCase() + "&ip=" + playerIp;
            URI uri = new URI(data);
            URL url = uri.toURL();
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            int responseCode = connection.getResponseCode();
            if (responseCode != 200) {
                getLogger().log(Level.WARNING, "Ошибка сервера: {0}", responseCode);
                return "error";
            }

            BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            Gson gson = new Gson();
            Answer answer = gson.fromJson(response.toString(), Answer.class);

            return answer.serverAnswer;

        } catch (Exception e) {
            e.printStackTrace();
        }
        return "error";
    }

    private void updateLastPlay(String playerNick, String playerIp) {
        try {
            String data = "quit?nickname=" + playerNick.toLowerCase() + "&ip=" + playerIp;
            URI uri = new URI(endpoint + data);
            URL url = uri.toURL();
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            int responseCode = connection.getResponseCode();
            if (responseCode != 200) {
                getLogger().log(Level.WARNING, "Ошибка сервера: {0}", responseCode);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void sendCode(String playerName) {
        try {
            URI uri = new URI(endpoint + "send");
            URL url = uri.toURL();
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);

            code = random.nextInt(90000) + 10000;

            String jsonInputString = "{\"user\": \"" + playerName + "\", \"code\": \"" + code + "\"}";

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsonInputString.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            int responseCode = conn.getResponseCode();
            if (responseCode == 200) {
                getLogger().log(Level.INFO, "Код отправлен игроку {0}", playerName);
            } else {
                getLogger().log(Level.WARNING, "Ошибка отправки: {0}", responseCode);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
