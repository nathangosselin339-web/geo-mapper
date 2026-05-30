package com.geomapping;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.block.BlockState;
import net.minecraft.util.ActionResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.Identifier;
import net.minecraft.registry.Registries;

import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GeoMappingMod implements ModInitializer {
    public static final Logger LOGGER = LoggerFactory.getLogger("geomapping");
    private static final String PYTHON_HOST = "127.0.0.1";
    private static final int PYTHON_PORT = 19528;

    @Override
    public void onInitialize() {
        LOGGER.info("GeoMapping mod initializing...");

        UseBlockCallback.EVENT.register((player, world, hand, hitResult) -> {
            if (world.isClient()) return ActionResult.PASS;
            if (player.getStackInHand(hand).isEmpty()) return ActionResult.PASS;

            BlockPos pos = hitResult.getBlockPos().offset(hitResult.getSide());
            BlockState state = world.getBlockState(pos);
            Identifier blockId = Registries.BLOCK.getId(state.getBlock());

            String json = String.format(
                "{\"type\":\"block_place\",\"x\":%d,\"y\":%d,\"z\":%d,\"block\":\"%s\"}",
                pos.getX(), pos.getY(), pos.getZ(), blockId.toString()
            );

            sendToPython(json);
            return ActionResult.PASS;
        });
    }

    private void sendToPython(String data) {
        try (Socket sock = new Socket(PYTHON_HOST, PYTHON_PORT);
             OutputStream out = sock.getOutputStream()) {
            out.write(data.getBytes(StandardCharsets.UTF_8));
            out.flush();
        } catch (Exception e) {
            LOGGER.warn("Failed to send to Python: {}", e.getMessage());
        }
    }
}
