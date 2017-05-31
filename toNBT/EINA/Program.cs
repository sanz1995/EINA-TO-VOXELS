using System;
using Substrate;
using Substrate.Nbt;
using Substrate.Core;
using System.IO;


namespace EINA
{
    class Program
    {
        static void Main (string[] args)
        {

            String dest = "resources/EINA_MAP";

            System.Console.WriteLine("Creating EINA map...");

            if (!Directory.Exists(dest))
                Directory.CreateDirectory(dest);


            NbtWorld world = AnvilWorld.Create(dest);

            world.Level.LevelName = "EINA";
            world.Level.Spawn = new SpawnPoint(20, 70, 20);
            world.Level.GameType = GameType.CREATIVE;

           
            IChunkManager cm = world.GetChunkManager();


            string[] lines = System.IO.File.ReadAllLines(@"../../cubos.txt");

            string[] words; 



            ChunkRef chunk;


            for (int i = 0; i < lines.Length; i++) {

                words = lines[i].Split(' ');
                int x = Int32.Parse(words[0]);
                int y = Int32.Parse(words[1]);
                int z = Int32.Parse(words[2]);
                int xLocal = x/32;
                int yLocal = y/32;
        

                if(!cm.ChunkExists(xLocal,yLocal)){
                    cm.CreateChunk(xLocal,yLocal);
                }
                chunk = cm.GetChunkRef(xLocal,yLocal);

                if(!chunk.IsDirty){

                    chunk.IsTerrainPopulated = true;
                    chunk.Blocks.AutoLight = false;
                    FlatChunk(chunk, 64);
                    chunk.Blocks.RebuildHeightMap();
                    chunk.Blocks.RebuildBlockLight();
                    chunk.Blocks.RebuildSkyLight();
                    //System.Console.WriteLine(chunk.IsDirty);
                    //System.Console.WriteLine("Creando "+xLocal+"  "+yLocal);
                    chunk.Blocks.SetID(x%16, z + 64, y%16, (int)BlockType.STONE);
                }else{
                    //chunk = cm.GetChunkRef(xLocal,yLocal);
                    //System.Console.WriteLine(x%16+"  "+y%16+"  "+(z+64));
                    chunk.Blocks.SetID(x%16, z + 64, y%16, (int)BlockType.STONE);

                }
            }

            world.Save();


        }

        static void FlatChunk (ChunkRef chunk, int height)
        {
            // Create bedrock
            for (int y = 0; y < 2; y++) {
                for (int x = 0; x < 16; x++) {
                    for (int z = 0; z < 16; z++) {
                        chunk.Blocks.SetID(x, y, z, (int)BlockType.BEDROCK);
                    }
                }
            }

            // Create stone
            for (int y = 2; y < height - 5; y++) {
                for (int x = 0; x < 16; x++) {
                    for (int z = 0; z < 16; z++) {
                        chunk.Blocks.SetID(x, y, z, (int)BlockType.STONE);
                    }
                }
            }

            // Create dirt
            for (int y = height - 5; y < height - 1; y++) {
                for (int x = 0; x < 16; x++) {
                    for (int z = 0; z < 16; z++) {
                        chunk.Blocks.SetID(x, y, z, (int)BlockType.DIRT);
                    }
                }
            }

            // Create grass
            for (int y = height - 1; y < height; y++) {
                for (int x = 0; x < 16; x++) {
                    for (int z = 0; z < 16; z++) {
                        chunk.Blocks.SetID(x, y, z, (int)BlockType.GRASS);
                    }
                }
            }
        }
    }
}
