using PaintDotNet;
using PaintDotNet.Effects;
using PaintDotNet.Imaging;
using PaintDotNet.PropertySystem;
using PaintDotNet.Rendering;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Windows.Forms;

namespace GeoMapperPlugin;

internal sealed class GeoMapperEffect : PropertyBasedBitmapEffect
{
    private static readonly ColorBgra32 GreenMark = new(0, 230, 0, 220);
    private static readonly ColorBgra32 RedMark = new(230, 0, 0, 220);

    private static readonly (string name, byte r, byte g, byte b)[] BlockColors = new[]
    {
        ("minecraft:white_wool", (byte)233, (byte)236, (byte)236),
        ("minecraft:orange_wool", (byte)240, (byte)118, (byte)19),
        ("minecraft:magenta_wool", (byte)189, (byte)68, (byte)179),
        ("minecraft:light_blue_wool", (byte)58, (byte)175, (byte)217),
        ("minecraft:yellow_wool", (byte)248, (byte)197, (byte)39),
        ("minecraft:lime_wool", (byte)112, (byte)185, (byte)25),
        ("minecraft:pink_wool", (byte)237, (byte)141, (byte)172),
        ("minecraft:gray_wool", (byte)63, (byte)68, (byte)71),
        ("minecraft:light_gray_wool", (byte)142, (byte)142, (byte)134),
        ("minecraft:cyan_wool", (byte)22, (byte)156, (byte)156),
        ("minecraft:purple_wool", (byte)137, (byte)50, (byte)184),
        ("minecraft:blue_wool", (byte)60, (byte)68, (byte)170),
        ("minecraft:brown_wool", (byte)131, (byte)84, (byte)50),
        ("minecraft:green_wool", (byte)94, (byte)124, (byte)22),
        ("minecraft:red_wool", (byte)176, (byte)46, (byte)38),
        ("minecraft:black_wool", (byte)29, (byte)29, (byte)33),
        ("minecraft:white_concrete", (byte)207, (byte)213, (byte)214),
        ("minecraft:orange_concrete", (byte)224, (byte)97, (byte)1),
        ("minecraft:magenta_concrete", (byte)169, (byte)48, (byte)159),
        ("minecraft:light_blue_concrete", (byte)36, (byte)137, (byte)199),
        ("minecraft:yellow_concrete", (byte)241, (byte)175, (byte)21),
        ("minecraft:lime_concrete", (byte)94, (byte)169, (byte)24),
        ("minecraft:pink_concrete", (byte)212, (byte)100, (byte)142),
        ("minecraft:gray_concrete", (byte)55, (byte)58, (byte)62),
        ("minecraft:light_gray_concrete", (byte)125, (byte)125, (byte)115),
        ("minecraft:cyan_concrete", (byte)21, (byte)137, (byte)145),
        ("minecraft:purple_concrete", (byte)100, (byte)32, (byte)156),
        ("minecraft:blue_concrete", (byte)45, (byte)47, (byte)143),
        ("minecraft:brown_concrete", (byte)96, (byte)60, (byte)31),
        ("minecraft:green_concrete", (byte)73, (byte)91, (byte)36),
        ("minecraft:red_concrete", (byte)142, (byte)33, (byte)33),
        ("minecraft:black_concrete", (byte)8, (byte)10, (byte)15),
        ("minecraft:oak_planks", (byte)162, (byte)129, (byte)72),
        ("minecraft:spruce_planks", (byte)115, (byte)87, (byte)54),
        ("minecraft:birch_planks", (byte)192, (byte)171, (byte)111),
        ("minecraft:dark_oak_planks", (byte)68, (byte)50, (byte)28),
        ("minecraft:acacia_planks", (byte)171, (byte)115, (byte)58),
        ("minecraft:cherry_planks", (byte)197, (byte)126, (byte)125),
        ("minecraft:stone", (byte)128, (byte)128, (byte)128),
        ("minecraft:cobblestone", (byte)116, (byte)116, (byte)116),
        ("minecraft:sandstone", (byte)220, (byte)211, (byte)168),
        ("minecraft:nether_bricks", (byte)44, (byte)28, (byte)28),
        ("minecraft:red_nether_bricks", (byte)135, (byte)50, (byte)34),
        ("minecraft:smooth_basalt", (byte)74, (byte)74, (byte)77),
        ("minecraft:polished_blackstone", (byte)50, (byte)46, (byte)54),
        ("minecraft:end_stone", (byte)217, (byte)217, (byte)191),
        ("minecraft:purpur_block", (byte)169, (byte)127, (byte)167),
        ("minecraft:prismarine", (byte)91, (byte)158, (byte)145),
        ("minecraft:dark_prismarine", (byte)44, (byte)84, (byte)66),
        ("minecraft:prismarine_bricks", (byte)98, (byte)167, (byte)155),
        ("minecraft:terracotta", (byte)160, (byte)97, (byte)66),
        ("minecraft:white_terracotta", (byte)210, (byte)178, (byte)161),
        ("minecraft:orange_terracotta", (byte)159, (byte)84, (byte)28),
        ("minecraft:magenta_terracotta", (byte)149, (byte)84, (byte)112),
        ("minecraft:light_blue_terracotta", (byte)112, (byte)108, (byte)138),
        ("minecraft:yellow_terracotta", (byte)186, (byte)133, (byte)35),
        ("minecraft:lime_terracotta", (byte)103, (byte)117, (byte)52),
        ("minecraft:pink_terracotta", (byte)161, (byte)77, (byte)78),
        ("minecraft:gray_terracotta", (byte)57, (byte)42, (byte)36),
        ("minecraft:light_gray_terracotta", (byte)135, (byte)106, (byte)97),
        ("minecraft:cyan_terracotta", (byte)86, (byte)91, (byte)92),
        ("minecraft:purple_terracotta", (byte)118, (byte)70, (byte)86),
        ("minecraft:blue_terracotta", (byte)73, (byte)59, (byte)91),
        ("minecraft:brown_terracotta", (byte)76, (byte)50, (byte)32),
        ("minecraft:green_terracotta", (byte)74, (byte)82, (byte)42),
        ("minecraft:red_terracotta", (byte)142, (byte)61, (byte)47),
        ("minecraft:black_terracotta", (byte)37, (byte)23, (byte)16),
        ("minecraft:gold_block", (byte)248, (byte)212, (byte)23),
        ("minecraft:iron_block", (byte)221, (byte)221, (byte)221),
        ("minecraft:diamond_block", (byte)90, (byte)201, (byte)205),
        ("minecraft:emerald_block", (byte)0, (byte)198, (byte)93),
        ("minecraft:redstone_block", (byte)180, (byte)2, (byte)2),
        ("minecraft:lapis_block", (byte)44, (byte)65, (byte)140),
        ("minecraft:netherite_block", (byte)66, (byte)55, (byte)55),
        ("minecraft:bone_block", (byte)227, (byte)221, (byte)200),
        ("minecraft:clay", (byte)161, (byte)161, (byte)167),
        ("minecraft:honeycomb_block", (byte)255, (byte)158, (byte)15),
        ("minecraft:ochre_froglight", (byte)217, (byte)174, (byte)69),
        ("minecraft:verdant_froglight", (byte)120, (byte)212, (byte)126),
        ("minecraft:pearlescent_froglight", (byte)192, (byte)144, (byte)207),
    };

    private static readonly string[] BlockNames;
    private static readonly byte[] BlockR;
    private static readonly byte[] BlockG;
    private static readonly byte[] BlockB;
    private static readonly int BlockCount;

    private static TcpListener? tcpListener;
    private static Thread? listenerThread;
    private static volatile bool isListenerRunning;
    private static readonly ConcurrentDictionary<(int wx, int wz), string> worldPlacements = new();

    private static int activePort = 19528;
    private static int activeOriginX;
    private static int activeOriginZ;
    private static double activeScale = 1.0;

    private static System.Windows.Forms.Timer? refreshTimer;
    private static bool isRealtimeEnabled;
    private static PropertyBasedEffectConfigToken? realtimeToken;

    static GeoMapperEffect()
    {
        BlockCount = BlockColors.Length;
        BlockNames = new string[BlockCount];
        BlockR = new byte[BlockCount];
        BlockG = new byte[BlockCount];
        BlockB = new byte[BlockCount];
        for (int i = 0; i < BlockCount; i++)
        {
            BlockNames[i] = BlockColors[i].name;
            BlockR[i] = BlockColors[i].r;
            BlockG[i] = BlockColors[i].g;
            BlockB[i] = BlockColors[i].b;
        }
    }

    private static string FindNearestBlock(byte r, byte g, byte b)
    {
        int bestDist = int.MaxValue;
        int bestIndex = 0;
        for (int i = 0; i < BlockCount; i++)
        {
            int dr = r - BlockR[i];
            int dg = g - BlockG[i];
            int db = b - BlockB[i];
            int dist = dr * dr + dg * dg + db * db;
            if (dist < bestDist)
            {
                bestDist = dist;
                bestIndex = i;
            }
        }
        return BlockNames[bestIndex];
    }

    private static void StartRefreshTimer()
    {
        if (refreshTimer is not null)
            return;

        refreshTimer = new System.Windows.Forms.Timer();
        refreshTimer.Interval = 500;
        refreshTimer.Tick += OnRefreshTick;
        refreshTimer.Start();
    }

    private static void StopRefreshTimer()
    {
        if (refreshTimer is not null)
        {
            refreshTimer.Stop();
            refreshTimer.Dispose();
            refreshTimer = null;
        }
        isRealtimeEnabled = false;
    }

    private static void OnRefreshTick(object? sender, EventArgs e)
    {
        if (!isRealtimeEnabled || realtimeToken is null)
        {
            StopRefreshTimer();
            return;
        }

        var form = Application.OpenForms.OfType<EffectConfigForm>().FirstOrDefault();
        if (form is null || form.IsDisposed)
        {
            StopRefreshTimer();
            return;
        }

        var newToken = (PropertyBasedEffectConfigToken)realtimeToken.Clone();
        int nextTick = realtimeToken.GetProperty<Int32Property>(PropertyNames.RefreshTick)!.Value + 1;
        newToken.SetPropertyValue(PropertyNames.RefreshTick, nextTick);
        form.Token = newToken;
        realtimeToken = newToken;
    }

    private static void StartTcpListener(int port, int originX, int originZ, double scale)
    {
        activePort = port;
        activeOriginX = originX;
        activeOriginZ = originZ;
        activeScale = scale;

        if (isListenerRunning)
            return;

        isListenerRunning = true;

        listenerThread = new Thread(() =>
        {
            try
            {
                tcpListener = new TcpListener(IPAddress.Loopback, port);
                tcpListener.Start();

                while (isListenerRunning)
                {
                    try
                    {
                        using var client = tcpListener.AcceptTcpClient();
                        var buffer = new byte[4096];
                        int bytesRead = client.GetStream().Read(buffer, 0, buffer.Length);
                        if (bytesRead > 0)
                        {
                            string json = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                            ProcessMessage(json);
                        }
                    }
                    catch (SocketException)
                    {
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"[GeoMapper TCP] {ex.Message}");
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[GeoMapper TCP] Listener error: {ex.Message}");
            }
        })
        { IsBackground = true };
        listenerThread.Start();
    }

    private static void ProcessMessage(string json)
    {
        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            if (root.TryGetProperty("type", out var typeEl) &&
                typeEl.GetString() == "block_place" &&
                root.TryGetProperty("x", out var xEl) &&
                root.TryGetProperty("z", out var zEl) &&
                root.TryGetProperty("block", out var blockEl))
            {
                int wx = xEl.GetInt32();
                int wz = zEl.GetInt32();
                string blockId = blockEl.GetString() ?? "minecraft:stone";
                worldPlacements[(wx, wz)] = blockId;
            }
        }
        catch
        {
        }
    }

    private enum PropertyNames
    {
        Port,
        OriginX,
        OriginZ,
        Scale,
        RealTime,
        RefreshTick
    }

    public GeoMapperEffect()
        : base(
            "GeoMapper",
            "GeoMapper",
            BitmapEffectOptions.Create() with
            {
                IsConfigurable = true
            })
    {
    }

    protected override PropertyCollection OnCreatePropertyCollection()
    {
        var props = new List<Property>();
        props.Add(new Int32Property(PropertyNames.Port, 19528, 1024, 65535));
        props.Add(new Int32Property(PropertyNames.OriginX, 0));
        props.Add(new Int32Property(PropertyNames.OriginZ, 0));
        props.Add(new DoubleProperty(PropertyNames.Scale, 1.0, 0.1, 100.0));
        props.Add(new BooleanProperty(PropertyNames.RealTime, false));
        props.Add(new Int32Property(PropertyNames.RefreshTick, 0, 0, int.MaxValue));
        return new PropertyCollection(props);
    }

    protected override void OnSetToken(PropertyBasedEffectConfigToken? newToken)
    {
        if (newToken is not null)
        {
            int port = newToken.GetProperty<Int32Property>(PropertyNames.Port)!.Value;
            int ox = newToken.GetProperty<Int32Property>(PropertyNames.OriginX)!.Value;
            int oz = newToken.GetProperty<Int32Property>(PropertyNames.OriginZ)!.Value;
            double sc = newToken.GetProperty<DoubleProperty>(PropertyNames.Scale)!.Value;

            StartTcpListener(port, ox, oz, sc);

            realtimeToken = newToken;
            bool realtime = newToken.GetProperty<BooleanProperty>(PropertyNames.RealTime)!.Value;

            if (realtime && !isRealtimeEnabled)
            {
                isRealtimeEnabled = true;
                StartRefreshTimer();
            }
            else if (!realtime && isRealtimeEnabled)
            {
                isRealtimeEnabled = false;
                StopRefreshTimer();
            }
        }
        base.OnSetToken(newToken);
    }

    protected override void OnRender(IBitmapEffectOutput output)
    {
        RectInt32 bounds = output.Bounds;

        using var srcBitmap = this.Environment.GetSourceBitmapBgra32();

        using var outputLock = output.LockBgra32();
        srcBitmap.CopyPixels(outputLock, bounds.Location);

        if (worldPlacements.IsEmpty)
            return;

        var outputSubRegion = outputLock.AsRegionPtr();
        var outputRegion = outputSubRegion.OffsetView(-bounds.Location);

        foreach (var kvp in worldPlacements)
        {
            if (IsCancelRequested) return;

            int pixelX = (int)((kvp.Key.wx - activeOriginX) / activeScale);
            int pixelY = (int)((kvp.Key.wz - activeOriginZ) / activeScale);

            if (pixelX < bounds.Left || pixelX >= bounds.Right ||
                pixelY < bounds.Top || pixelY >= bounds.Bottom)
                continue;

            ColorBgra32 src = outputRegion[pixelX, pixelY];
            string expected = FindNearestBlock(src.R, src.G, src.B);
            if (kvp.Value == expected)
                outputRegion[pixelX, pixelY] = GreenMark;
            else
                outputRegion[pixelX, pixelY] = RedMark;
        }
    }
}
