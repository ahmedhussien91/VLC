# Configuration
from cgitb import text


# input 
# Sampling table ->  {'Sample':'Value'}

class runlenght:

    def encode(self, text):

        """
        Returns a run-length encoded string from an input string.
        Note: This function will not return the character count in the return
        string if only a single instance of the character is found.

        Args:
            text (str): A string to encode

        Returns:
            str: A run length encoded string

        Example:
            input: "aaabbcdddd"
            returns: "3a2b1c4d"
        """

        count = 1
        previous = ""
        mapping = list()

        for character in text:
            if character != previous:
                if previous:
                    mapping.append((previous, count))
                count = 1
                previous = character
            else:
                count += 1
        else:
            mapping.append((character, count))

        result = ""

        for character, count in mapping:
                result += str(count)
                result += character

        return result
    
    def decode(self, text):
        
        """
        Returns a decoded string from an input runlength encoded string.
        Note: This function will not return the character count in the return
        string if only a single instance of the character is found.

        Args:
            text (str): A run length encoded string

        Returns:
            str: A string to encode

        Example:
            input: "3a2b1c4d"
            returns: "aaabbcdddd"
        """
        result= ""
        isCount = True
        for character in text:
            if isCount:
                count = int(character)
                isCount = False
            else:
                for i in range(count):
                    result += character
                isCount = True                

        return result



if __name__ == "__main__":
    runlenghtEncoder = runlenght()
encoded_str = runlenghtEncoder.encode("aaabbcdddd")
print(encoded_str)
print(runlenghtEncoder.decode(encoded_str))